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

  const rank = useRank({
    refreshInterval: 3000,
    focusThrottleInterval: 3000,
    dedupingInterval: 3000,
  });

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        p: '50px',
        minHeight: 'calc(100vh - 100px)',
        justifyContent: bottom ? 'flex-end' : 'flex-start',
      }}
    >
      {rank.data?.summaries
        .slice(0, limit)
        .map((summary) => <TeamRow key={summary.name} summary={summary} />)}
    </Box>
  );
}

function TeamRow({ summary }: { summary: TeamSummary }): React.ReactElement {
  return (
    <Box sx={{ display: 'flex', background: '#f5f5f5' }}>
      <Box
        sx={{
          flex: '0 0 30px',
          textAlign: 'center',
          p: 1,
          background: '#273',
          color: '#fff',
          fontWeight: 'bold',
        }}
      >
        {summary.currentRank}
      </Box>
      <Box
        sx={{
          flex: '1 0 100px',
          p: 1,
          overflow: 'hidden',
          height: '1em',
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
        }}
      >
        <HiAcademicCap />
      </Box>
      <Box
        sx={{
          flex: '0 0 70px',
          textAlign: 'right',
          p: 1,
          fontWeight: 'bold',
          height: '1em',
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
