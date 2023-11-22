import Box from '@mui/joy/Box';
import Typography from '@mui/joy/Typography';
import React from 'react';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';
import { GoTriangleRight } from 'react-icons/go';
import { HiAcademicCap } from 'react-icons/hi2';
import { TeamSummary, useRank } from '~/utils/hooks';

export default function ChangesPage(): React.ReactElement {
  const rank = useRank({
    refreshInterval: 3000,
    focusThrottleInterval: 3000,
    dedupingInterval: 3000,
  });

  const changes = rank.data?.summaries
    .filter((summary) => summary.rankChanged && summary.scoreChanged)
    .slice(0, 10);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        p: 2,
        height: 'calc(100vh - 32px)',
        justifyContent: 'flex-end',
      }}
      gap="5px"
    >
      {changes?.map((summary) => (
        <ChangeRow key={summary.name} summary={summary} />
      ))}
      <ChangeRow
        summary={{
          name: 'Dummy',
          currentRank: 123,
          lastRank: 123,
          currentScore: 100,
          lastScore: 90,
          rankChanged: true,
          scoreChanged: true,
        }}
      />
    </Box>
  );
}

function ChangeRow({ summary }: { summary: TeamSummary }): React.ReactElement {
  const scoreChanges = summary.currentScore - summary.lastScore;
  const isScoreUp = scoreChanges > 0;
  const isRankUp = summary.currentRank > summary.lastRank;

  return (
    <Box
      sx={{
        display: 'flex',
        background: '#f5f5f5',
        overflow: 'hidden',
        borderRadius: '5px',
      }}
    >
      {/****** RANK ******/}
      <Box
        sx={{
          flex: '0 0 60px',
          display: 'flex',
          flexDirection: 'column',
          textAlign: 'center',
          background: isRankUp ? '#c44' : '#39c',
          color: '#fff',
          fontWeight: 'bold',
          justifyContent: 'center',
        }}
      >
        <Box
          sx={{
            alignItems: 'center',
            height: '20px',
            display: 'flex',
            alignContent: 'center',
            justifyContent: 'center',
            fontSize: '20px',
          }}
        >
          {isRankUp ? <FaArrowUp /> : <FaArrowDown />}
        </Box>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.8em',
          }}
        >
          <div>{summary.lastRank}</div>
          <GoTriangleRight
            size="1em"
            style={{ paddingTop: '3px', margin: '0 -2px 0 -1px' }}
          />
          <div>{summary.currentRank}</div>
        </Box>
      </Box>
      {/****** TEAM NAME ******/}
      <Box
        sx={{
          flex: '1 0 100px',
          p: 1,
          overflow: 'hidden',
          height: '2em',
          lineHeight: '2em',
          whiteSpace: 'nowrap',
          textOverflow: 'ellipsis',
        }}
      >
        {summary.name}
      </Box>
      {/****** IS ACADEMIC ******/}
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
      {/****** SCORES ******/}
      <Box
        sx={{
          flex: '0 0 100px',
          textAlign: 'right',
          px: 2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'right',
          justifyContent: 'center',
        }}
        gap="5px"
      >
        <Typography
          level="body-md"
          sx={{
            fontWeight: 'bold',
            height: '1em',
          }}
        >
          {summary.currentScore}
        </Typography>
        <Typography
          level="body-xs"
          sx={{
            color: isScoreUp ? '#c44' : '#39c',
          }}
        >{`${isScoreUp ? '+' : ''}${scoreChanges}`}</Typography>
      </Box>
    </Box>
  );
}
