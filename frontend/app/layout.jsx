import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AI-Powered Resume | Interactive Portfolio',
  description: 'An intelligent resume platform with AI-powered query capabilities using RAG technology.',
  keywords: 'resume, portfolio, AI, RAG, full-stack developer, machine learning',
  authors: [{ name: 'AI Resume Assistant' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}
