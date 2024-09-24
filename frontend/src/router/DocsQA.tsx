import React, { Suspense, lazy } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import type { BreadcrumbsRoute } from 'use-react-router-breadcrumbs'

import ScreenFallbackLoader from '@/components/base/molecules/ScreenFallbackLoader'
import DataHub from '@/screens/dashboard/docsqa/DataSources'
import DashboardNavBar from '@/screens/dashboard/docsqa/DashboardNavBar'
import Applications from '@/screens/dashboard/docsqa/Applications'
const Home = lazy(() => import('@/screens/home'))
const DocsQA = lazy(() => import('@/screens/dashboard/docsqa'))
const DocsQAChatbot = lazy(() => import('@/screens/dashboard/docsqa/Chatbot'))
const DocsQASettings = lazy(() => import('@/screens/dashboard/docsqa/settings'))

const FallBack = () => (
  <div className="flex flex-1">
    <ScreenFallbackLoader />
  </div>
)

const DashboardLayout = () => {
  const location = useLocation()
  const shouldRenderNavBar = !location.pathname.includes('apps')

  return (
    <div className="flex flex-col h-full">
      {shouldRenderNavBar && <DashboardNavBar />}
      <Suspense fallback={<FallBack />}>
        <div className="p-4 bg-[#fafcff] h-full">
          <Outlet />
        </div>
      </Suspense>
    </div>
  )
}

const MainLayout = () => {
  const location = useLocation()
  const shouldRenderNavBar = !location.pathname.includes('apps')

  return (
    <div className="flex flex-col h-full">
      {shouldRenderNavBar && <NavBar />}
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
    path: '/dashboard',
    element: <DashboardLayout />,
    children: [
      {
        path: '/dashboard/collections',
        children: [{ index: true, element: <DocsQASettings /> }],
      },
      {
        path: '/dashboard/data-sources',
        children: [{ index: true, element: <DataHub /> }],
      },
      {
        path: '/dashboard/applications',
        children: [{ index: true, element: <Applications /> }],
      },
      {
        path: '/dashboard/*',
        children: [{ index: true, element: <DocsQA /> }],
      },
    ],
  },
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        path: '/*',
        children: [{ index: true, element: <Home /> }],
      },
      {
        path: '/apps/:id',
        children: [{ index: true, element: <DocsQAChatbot /> }],
      },
    ]
  }
]

export default routes
