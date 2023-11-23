/* eslint-disable @typescript-eslint/explicit-module-boundary-types */

import React from 'react';
import useSWR, { type SWRConfiguration } from 'swr';
import { fetchMockGraph } from './mock';
import { GraphDataResponse, Ranking, Team } from './types';

export function useGraph(config?: SWRConfiguration) {
  return useSWR('/contest/graph/', fetchGraph, config);
}

function fetchGraph(): Promise<GraphDataResponse> {
  const d = (new Date().valueOf() / 1000) | 0;
  const ts = d - (d % 5);
  return fetch(`/contest/graph/?ts=${ts}`).then((response) => response.json());
}

export function useRank(useDummy: boolean, config?: SWRConfiguration) {
  const ref = React.useRef(fetchMockGraph());
  const lsat = React.useRef<Ranking[]>();
  return useSWR(
    '/contest/graph/?summary',
    async () => {
      const current = await (useDummy ? ref.current() : fetchGraph());
      const summaries = teamAggsToSummary(current.ranking, lsat.current);
      lsat.current = current.ranking;
      return { summaries };
    },
    config,
  );
}

export interface TeamSummary {
  team: Team;
  currentRank: number;
  currentScore: number;
  lastRank: number;
  lastScore: number;
  rankChanged: boolean;
  scoreChanged: boolean;
}

// function convertToAggs(datasets: GraphDataset[]): Ranking[] {
//   const aggs: Ranking[] = [];
//   datasets.forEach((dataset) => {
//     const latestScore =
//       dataset.data.length > 0
//         ? dataset.data[dataset.data.length - 1]
//         : undefined;

//     const agg: Ranking = {
//       name: dataset.label,
//       rank: 0,
//       score: latestScore?.y || 0,
//     };

//     aggs.push(agg);
//   });

//   const latestRanks = aggs
//     .map((agg, index) => ({ index, agg }))
//     .sort((a, b) => b.agg.score - a.agg.score);
//   for (let i = 0; i < latestRanks.length; i++) {
//     latestRanks[i].agg.rank = i + 1;
//   }
//   aggs.sort((a, b) => a.rank - b.rank);

//   return aggs;
// }

function teamAggsToSummary(
  currentAggs: Ranking[],
  lastAggs: Ranking[] | undefined,
): TeamSummary[] {
  const summaries: TeamSummary[] = [];
  for (const agg of currentAggs) {
    const lastAgg = lastAggs?.find(
      (lastAgg) => lastAgg.team.id === agg.team.id,
    );
    const summary: TeamSummary = {
      team: agg.team,
      currentRank: agg.rank,
      currentScore: agg.latest_score,
      lastRank: lastAgg?.rank ?? agg.rank,
      lastScore: lastAgg?.latest_score ?? agg.latest_score,
      rankChanged: false,
      scoreChanged: false,
    };
    summaries.push(summary);
  }

  for (const summary of summaries) {
    summary.rankChanged = summary.currentRank !== summary.lastRank;
    summary.scoreChanged = summary.currentScore !== summary.lastScore;
  }

  summaries.sort((a, b) => a.currentRank - b.currentRank);

  return summaries;
}
