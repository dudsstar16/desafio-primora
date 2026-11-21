import { lazy, StrictMode, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './styles.css'

const Presentation = lazy(() => import('./App'))
const Dashboard = lazy(() => import('./dashboard/Dashboard'))
const isDashboard = /^\/dashboard\/?$/.test(window.location.pathname)
const Page = isDashboard ? Dashboard : Presentation

if (isDashboard) document.title = 'Painel operacional · Distribuidora Vetor'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: 1 } },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Suspense fallback={<main id="conteudo" tabIndex={-1} style={{ color: 'var(--cream)', padding: '2rem' }}>Carregando…</main>}>
        <Page />
      </Suspense>
    </QueryClientProvider>
  </StrictMode>,
)
