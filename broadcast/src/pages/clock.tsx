import Box from '@mui/joy/Box';
import React from 'react';
import { useGraph } from '~/utils/hooks';

export default function ClockPage(): React.ReactElement {
  const graph = useGraph({});

  const [start, end] = React.useMemo(
    () =>
      graph.data
        ? [new Date(graph.data.graph_min), new Date(graph.data.graph_max)]
        : [new Date(), new Date()],
    [graph.data?.graph_min, graph.data?.graph_max],
  );

  const [now, setNow] = React.useState({
    progress: 0,
    remainStr: '00:00:00',
    remain: 0,
  });
  React.useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      const progress =
        (now.getTime() - start.getTime()) / (end.getTime() - start.getTime());
      const remain = Math.round(end.getTime() - now.getTime());
      const remainStr = new Date(remain).toISOString().substring(11, 19);
      // .substring(11, 23);
      setNow({ progress, remainStr, remain });
    }, 100);
    return () => clearInterval(timer);
  }, [start, end]);

  return (
    <Box
      sx={{
        background: '#fff',
        color: '#273',
        border: '1px solid #273',
        borderRadius: '8px',
        textAlign: 'center',
        padding: '10px 20px',
      }}
    >
      <Box
        sx={{
          fontSize: '100px',
          lineHeight: 1,
          fontWeight: 'bold',
          WebkitFontFeatureSettings: 'hwid',
        }}
      >
        {now.remainStr}
      </Box>
      <Box
        sx={{
          height: '8px',
          background: '#ddd',
          borderRadius: '8px',
          margin: '10px 0 5px',
        }}
      >
        <Box
          sx={{
            height: '100%',
            background: `${now.remain < 1000 * 3600 ? '#f44' : '#273'}`,
            borderRadius: '8px',
            width: `${now.progress * 100}%`,
          }}
        />
      </Box>
    </Box>
  );
}
