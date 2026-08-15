import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import LandingPage from './LandingPage.tsx'

const showApplication = new URLSearchParams(window.location.search).has('app')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {showApplication ? <App /> : <LandingPage onEnterApp={() => { window.location.search = '?app=1' }} />}
  </StrictMode>,
)
