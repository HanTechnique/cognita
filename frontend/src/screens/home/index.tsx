import React from 'react'
import icon from '@/assets/img/errors/404.svg'

const Home = () => {
  return (
    <div className="w-full h-screen grid place-items-center">
      <div className="flex flex-col sm:flex-row gap-4 items-center sm:pb-72">
        <img src={icon} />
        <div className="divider sm:divider-horizontal" />
        <div className="flex flex-col gap-2">
          <h2 className="font-inter font-black text-6xl">Home Page</h2>
          <p className="font-semibold">
            You are currently in the home page.
            <br />
            If you want to go to the dashboard please click the below link.
            <br />
            <a
              className="link text-primary"
              href="/dashboard"
            >
              Dashboard
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Home
