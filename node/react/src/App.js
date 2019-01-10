import React, { Component } from 'react'
import Cities from './Cities'

import logo from './logo.svg'
import './App.css'

class App extends Component {
  render() {
    const { auth } = this.props

    // if we are not logged in, then show the login dialog
    if (window.location.pathname !== '/callback' && !auth.isAuthenticated()) {
      auth.login()
    }

    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome to Maana Q - React</h1>
        </header>
        {window.location.pathname === '/callback' || !auth.isAuthenticated() ? (
          // don't try and load the Cities if we are still working on authentication
          <div />
        ) : (
          // load and show the Cities
          <Cities />
        )}
      </div>
    )
  }
}

export default App
