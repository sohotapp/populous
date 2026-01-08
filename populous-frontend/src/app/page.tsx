import { redirect } from 'next/navigation'

// Redirect root to projects dashboard
export default function HomePage() {
  redirect('/projects')
}
