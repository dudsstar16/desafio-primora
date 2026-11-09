"""
Etapa 5 do ETL: Testes Automatizados (Compatível com Pytest e Unittest nativo)
Testa todas as regras de limpeza (CNPJ, Telefone, Data, CEP, Bairros e Guardrails)
usando chamadas simuladas (mocks) para a API de CEP, como exigido no PDF do desafio.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from etl.transform_fields import normalize_cnpj, normalize_phone, normalize_date
from etl.cep_service import CepService
from etl.transform_address import canonicalize_neighborhood_name, resolve_address


class TestEtlNormalizationAndGuardrails(unittest.TestCase):
    """
    Suíte completa de testes automatizados do Pipeline ETL.
    Roda tanto com `pytest` quanto com `python -m unittest -v`.
    """

    def test_normalize_cnpj_preserves_leading_and_trailing_zeros_as_text(self):
        # CNPJ que começa com 0
        cnpj_clean, rule = normalize_cnpj("04.711.671/9022-94")
        self.assertIsInstance(cnpj_clean, str)
        self.assertEqual(cnpj_clean, "04711671902294")
        self.assertEqual(len(cnpj_clean), 14)
        self.assertEqual(rule, "LIMPEZA_MASCARA_CNPJ_PARA_TEXTO_14_DIGITOS")

        # CNPJ que já estava só com números e termina com 0
        cnpj_clean2, rule2 = normalize_cnpj("19693792374740")
        self.assertEqual(cnpj_clean2, "19693792374740")
        self.assertIsNone(rule2)

    def test_normalize_phone_removes_country_code_and_keeps_trailing_zeros(self):
        # Telefone com +55, espaços e traço
        phone1, rule1 = normalize_phone("+55 61 95386-2084")
        self.assertEqual(phone1, "61953862084")
        self.assertEqual(rule1, "PADRONIZACAO_TELEFONE_TEXTO_DDD_NUMERO")

        # Telefone que termina em 00 (não pode perder zeros!)
        phone2, rule2 = normalize_phone("61970855700")
        self.assertIsInstance(phone2, str)
        self.assertEqual(phone2, "61970855700")
        self.assertIsNone(rule2)

        # Telefone fixo com parênteses
        phone3, rule3 = normalize_phone("(61) 3491-1634")
        self.assertEqual(phone3, "6134911634")
        self.assertEqual(rule3, "PADRONIZACAO_TELEFONE_TEXTO_DDD_NUMERO")

    def test_normalize_date_handles_iso_br_and_english_formats(self):
        # Formato ISO já limpo
        d1, r1 = normalize_date("2022-06-21")
        self.assertEqual(d1, "2022-06-21")
        self.assertIsNone(r1)

        # Formato BR com barra e com traço
        d2, r2 = normalize_date("28/02/2022")
        self.assertEqual(d2, "2022-02-28")
        self.assertEqual(r2, "CONVERSAO_DATA_BR_PARA_ISO")

        d3, r3 = normalize_date("08-01-2022")
        self.assertEqual(d3, "2022-01-08")
        self.assertEqual(r3, "CONVERSAO_DATA_BR_PARA_ISO")

        # Formato Inglês maiúsculo e minúsculo
        d4, r4 = normalize_date("Dec 24, 2023")
        self.assertEqual(d4, "2023-12-24")
        self.assertEqual(r4, "CONVERSAO_DATA_TEXTO_INGLES_PARA_ISO")

        d5, r5 = normalize_date("jul 21, 2022")
        self.assertEqual(d5, "2022-07-21")
        self.assertEqual(r5, "CONVERSAO_DATA_TEXTO_INGLES_PARA_ISO")

    def test_canonicalize_neighborhood_variations(self):
        cases = [
            ("Sul (Águas Claras)", "Águas Claras"),
            ("Norte (Aguas Claras)", "Águas Claras"),
            ("aguas claras", "Águas Claras"),
            ("Águas Claras/DF", "Águas Claras"),
            ("Taguatinga - DF", "Taguatinga"),
            ("taguatinga sul", "Taguatinga"),
            ("TAGUATINGA", "Taguatinga"),
            ("V. Pires", "Vicente Pires"),
            ("Vte Pires", "Vicente Pires"),
            ("Setor Habitacional Vicente Pires", "Vicente Pires"),
            ("guara - df", "Guará"),
            ("Guará I", "Guará"),
            ("Guará II", "Guará"),
        ]
        for raw_input, expected in cases:
            with self.subTest(raw_input=raw_input):
                self.assertEqual(canonicalize_neighborhood_name(raw_input), expected)

    def test_cep_service_uses_mocked_api_without_real_internet(self):
        """
        Simula uma chamada HTTP ao ViaCEP para um CEP inédito ('70040010')
        garantindo que o teste não usa internet real (exigência do PDF).
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_cache = Path(tmp_dir) / "temp_cep_cache.json"
            service = CepService(cache_path=temp_cache, allow_network=True)

            fake_response = MagicMock()
            fake_response.status_code = 200
            fake_response.json.return_value = {
                "cep": "70040-010",
                "logradouro": "Avenida Teste",
                "bairro": "Sul (Águas Claras)",
                "localidade": "Brasília",
                "uf": "DF",
            }

            with patch("etl.cep_service.requests.get", return_value=fake_response) as mock_get:
                result = service.lookup_cep("70040010")
                self.assertIsNotNone(result)
                self.assertEqual(result["bairro_api"], "Sul (Águas Claras)")
                self.assertEqual(mock_get.call_count, 1)

                # Segunda chamada ao mesmo CEP deve vir do Cache Local (sem chamar requests.get de novo!)
                result_cached = service.lookup_cep("70040010")
                self.assertEqual(result_cached["bairro_api"], "Sul (Águas Claras)")
                self.assertEqual(mock_get.call_count, 1)

    def test_guardrail_conflict_cep_wins_over_typed_neighborhood(self):
        """
        Testa o Guardrail principal: Cliente digitou 'Sul (Aguas Claras)',
        mas o serviço de consulta retorna 'Taguatinga' para o CEP '72140-010'.
        O resultado da consulta deve vencer e gerar log de conflito na auditoria.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = CepService(cache_path=Path(tmp_dir) / "cache.json", allow_network=False)
            res = resolve_address("Sul (Aguas Claras)", "72140-010", service)

            self.assertEqual(res["cep_normalizado"], "72140010")
            self.assertEqual(res["bairro_normalizado"], "Taguatinga")
            self.assertIn("GUARDRAIL_CONFLITO_CEP_VENCEU_TEXTO", res["regra_bairro"] or "")

    def test_invalid_or_missing_cep_falls_back_to_dictionary_and_logs_audit(self):
        """
        Testa clientes com CEP '00000-000' ou sem CEP (ex: Guará II),
        garantindo que o CEP vira None e o bairro é salvo pelo dicionário.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = CepService(cache_path=Path(tmp_dir) / "cache.json", allow_network=False)

            # Caso 1: CEP inválido 00000-000
            res_invalid = resolve_address("Taguatinga/DF", "00000-000", service)
            self.assertIsNone(res_invalid["cep_normalizado"])
            self.assertEqual(res_invalid["regra_cep"], "CEP_INVALIDO_DESCARTADO")
            self.assertEqual(res_invalid["bairro_normalizado"], "Taguatinga")

            # Caso 2: Guará sem CEP
            res_guara = resolve_address("Guará II", "", service)
            self.assertIsNone(res_guara["cep_normalizado"])
            self.assertEqual(res_guara["regra_cep"], "CEP_AUSENTE")
            self.assertEqual(res_guara["bairro_normalizado"], "Guará")

            # Caso 3: Sem bairro e sem CEP (CLI0047)
            res_empty = resolve_address("", "", service)
            self.assertIsNone(res_empty["cep_normalizado"])
            self.assertEqual(res_empty["bairro_normalizado"], "Não Informado")
            self.assertEqual(res_empty["regra_bairro"], "BAIRRO_E_CEP_AUSENTES_DEFINIDO_NAO_INFORMADO")


if __name__ == "__main__":
    unittest.main()

