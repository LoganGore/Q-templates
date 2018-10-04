import React from "react";
import { compose, graphql, withApollo } from "react-apollo";
import gql from "graphql-tag";

const ServiceInfoFragment = gql`
  fragment ServiceInfo on Service {
    id
    name
    thumbnailUrl
    tags
    endpointUrl
    subscriptionEndpointUrl
    status
    lastChecked
    isSystem
  }
`;

const AllServicesQuery = gql`
  query {
    allServices {
      ...ServiceInfo
    }
  }
  ${ServiceInfoFragment}
`;

const Services = ({ data }) => {
  if (data.error) {
    return (
      <div className="Data-error">Error: {JSON.stringify(data.error)}</div>
    );
  }
  if (data.loading) {
    return <div className="Data-load">Loading...</div>;
  }

  const Item = props => {
    const { service } = props;
    return <li>{service.name}</li>;
  };

  return (
    <div>
      <p className="App-intro">Maana Services</p>
      <ul className="Service-list">
        {data.allServices.map(s => <Item key={s.id} service={s} />)}
      </ul>
    </div>
  );
};

const enhancers = compose(
  graphql(AllServicesQuery),
  withApollo
);
export default enhancers(Services);
