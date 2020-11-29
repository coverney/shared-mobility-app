import React from 'react';
import DataVisualization from './components/DataVisualization';
import { Route, Switch, Redirect } from 'react-router-dom';

export const Routes = () => {
  return (
    <div>
      <Route exact path="/data" component={DataVisualization} />
    </div>
  );
};
