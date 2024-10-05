import React, { Suspense, lazy } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import type { BreadcrumbsRoute } from 'use-react-router-breadcrumbs'

import ScreenFallbackLoader from '@/components/base/molecules/ScreenFallbackLoader'
import DataHub from '@/screens/dashboard/docsqa/DataSources'
import NavBar from '@/screens/home/NavBar'
import Applications from '@/screens/dashboard/docsqa/Applications'
const Home = lazy(() => import('@/screens/home'))
const Login = lazy(() => import('@/screens/login'))
const DocsQA = lazy(() => import('@/screens/dashboard/docsqa'))
const DocsQAChatbot = lazy(() => import('@/screens/dashboard/docsqa/Chatbot'))
const DocsQASettings = lazy(() => import('@/screens/dashboard/docsqa/settings'))
import PrivateRoute from '@/components/PrivateRoute'; // Assuming PrivateRoute is in the same directory
import { AuthProvider } from '@/components/AuthContext'

const FallBack = () => (
  <div className="flex flex-1">
    <ScreenFallbackLoader />
  </div>
)

const MainLayout = () => {
  const location = useLocation()
  const shouldRenderNavBar = !location.pathname.includes('apps')

  return (
    <div className="flex flex-col h-full">
      {shouldRenderNavBar && 
      <AuthProvider><NavBar /></AuthProvider>}
      <Suspense fallback={<FallBack />}>
        <div className="p-4 bg-[#fafcff] h-full">
          <Outlet />
        </div>
      </Suspense>
    </div>
  )
}

export const routes = (): BreadcrumbsRoute[] => [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        path: '/dashboard/collections',
        children: [{ index: true, element: (
          <PrivateRoute>
            <DocsQASettings />
          </PrivateRoute>
        ) }],
      },
      {
        path: '/dashboard/data-sources',
        children: [{ index: true, element: (
          <PrivateRoute>
            <DataHub />
          </PrivateRoute>
        ) }],
      },
      {
        path: '/dashboard/applications',
        children: [{ index: true, element: (
          <PrivateRoute>
            <Applications />
          </PrivateRoute>
        ) }],
      },
      {
        path: '/apps/:id',
        children: [{ index: true, element: (
          <PrivateRoute>
            <DocsQAChatbot />
          </PrivateRoute>
        ) }],
      },
      {
        path: '/login',
        children: [{ index: true, element: <Login /> }],
      },
      {
        path: '/dashboard/*',
        children: [{ index: true, element: (
          <PrivateRoute>
            <DocsQA />
          </PrivateRoute>
        ),
        }],
      },
      {
        path: '*',
        children: [{ index: true, element: <Home /> }],
      },
    ],
  },
]

export default routes
