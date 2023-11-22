import { CssVarsProvider } from '@mui/joy/styles';
import React, { Suspense } from 'react';
import { useRoutes } from 'react-router-dom';
import { SWRConfig } from 'swr';
import routes from '~react-pages';

export function App(): React.ReactElement {
  const routeContent = useRoutes(routes);
  return (
    <CssVarsProvider defaultMode="light">
      <SWRConfig
        value={{
          focusThrottleInterval: 20000,
          dedupingInterval: 10000,
        }}
      >
        <Suspense fallback={<p>Loading...</p>}>{routeContent}</Suspense>
      </SWRConfig>
    </CssVarsProvider>
  );
}
