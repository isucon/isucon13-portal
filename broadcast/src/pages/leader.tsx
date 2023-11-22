import Box from '@mui/joy/Box';
import React from 'react';
import { HiAcademicCap } from 'react-icons/hi2';
import { useSearchParams } from 'react-router-dom';
import { formatScore } from '~/utils/format';
import { TeamSummary, useRank } from '~/utils/hooks';

export default function RankPage(): React.ReactElement {
  const [searchParams] = useSearchParams();
  const limit = parseInt(searchParams.get('limit') ?? '15') || 15;
  const bottom = !!(parseInt(searchParams.get('bottom') ?? '0') || 0);
  const dummy = !!(parseInt(searchParams.get('dummy') ?? '0') || 0);

  const rank = useRank(dummy, {
    refreshInterval: 3000,
    focusThrottleInterval: 3000,
    dedupingInterval: 3000,
  });

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        px: '50px',
        py: '25px',
        minHeight: 'calc(100vh - 50px)',
        justifyContent: bottom ? 'flex-end' : 'flex-start',
      }}
      gap="2px"
    >
      {rank.data?.summaries
        .slice(0, limit)
        .map((summary) => <TeamRow key={summary.name} summary={summary} />)}
    </Box>
  );
}

function TeamRow({ summary }: { summary: TeamSummary }): React.ReactElement {
  const innerPadding = '5px';

  return (
    <Box
      sx={{
        display: 'flex',
        background: /* #f5f5f5 */ 'rgba(255,255,255,0.9)',
      }}
    >
      <Box
        sx={{
          flex: '0 0 30px',
          textAlign: 'center',
          px: '10px',
          py: innerPadding,
          background: '#273',
          color: '#fff',
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {summary.currentRank}
      </Box>
      <Box
        sx={{
          flex: '1 0 100px',
          px: '15px',
          py: innerPadding,
          overflow: 'hidden',
          whiteSpace: 'nowrap',
          textOverflow: 'ellipsis',
        }}
      >
        {summary.name}
      </Box>
      <Box
        sx={{
          flex: '0 0 30px',
          background: '#777',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: '15px',
        }}
      >
        <HiAcademicCap />
      </Box>
      <Box
        sx={{
          flex: '0 0 70px',
          textAlign: 'right',
          px: '10px',
          py: innerPadding,
          fontWeight: 'bold',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* {summary.scoreChanged ? (
          <>
            <Typography level="body-xs" sx={{ display: 'inline' }}>
              {`${summary.lastScore}→ `}
            </Typography>
            {summary.currentScore}
          </>
        ) : ( */}
        <>{formatScore(summary.currentScore)}</>
        {/* )} */}
      </Box>
    </Box>
  );
}
