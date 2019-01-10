import React from 'react'
import { compose, graphql, withApollo } from 'react-apollo'
import gql from 'graphql-tag'

const AllServicesQuery = gql`
  query {
    allCitys {
      name
    }
  }
`

const Services = ({ data }) => {
  if (data.error) {
    return <div className="Data-error">Error: {JSON.stringify(data.error)}</div>
  }
  if (data.loading) {
    return <div className="Data-load">Loading...</div>
  }

  const Item = props => {
    const { service } = props
    return <li>{service.name}</li>
  }

  return (
    <div>
      <p className="App-intro">Maana Services</p>
      <ul className="Service-list">
        {data.allCitys.map(s => (
          <Item key={s.name} service={s} />
        ))}
      </ul>
    </div>
  )
}

const enhancers = compose(
  graphql(AllServicesQuery),
  withApollo
)
export default enhancers(Services)
