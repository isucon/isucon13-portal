/* eslint-disable @typescript-eslint/explicit-module-boundary-types */

import React from 'react';
import useSWR, { type SWRConfiguration } from 'swr';
import { fetchMockGraph } from './mock';
import { GraphDataResponse, GraphDataset } from './types';

export function useGraph(config?: SWRConfiguration) {
  return useSWR('/contest/graph/', fetchGraph, config);
}

function fetchGraph(): Promise<GraphDataResponse> {
  return fetch('/contest/graph/').then((response) => response.json());
}

export function useRank(useDummy: boolean, config?: SWRConfiguration) {
  const ref = React.useRef(fetchMockGraph());
  const lsat = React.useRef<TeamCurrentAggs[]>();
  return useSWR(
    '/contest/graph/?summary',
    async () => {
      const current = await (useDummy ? ref.current() : fetchGraph());
      const aggs = convertToAggs(current.graph_datasets);
      const summaries = teamAggsToSummary(aggs, lsat.current);
      lsat.current = aggs;
      return { summaries };
    },
    config,
  );
}

interface TeamCurrentAggs {
  name: string;
  rank: number;
  score: number;
}

export interface TeamSummary {
  name: string;
  currentRank: number;
  currentScore: number;
  lastRank: number;
  lastScore: number;
  rankChanged: boolean;
  scoreChanged: boolean;
}

function convertToAggs(datasets: GraphDataset[]): TeamCurrentAggs[] {
  const aggs: TeamCurrentAggs[] = [];
  datasets.forEach((dataset) => {
    const latestScore =
      dataset.data.length > 0
        ? dataset.data[dataset.data.length - 1]
        : undefined;

    const agg: TeamCurrentAggs = {
      name: dataset.label,
      rank: 0,
      score: latestScore?.y || 0,
    };

    aggs.push(agg);
  });

  const latestRanks = aggs
    .map((agg, index) => ({ index, agg }))
    .sort((a, b) => b.agg.score - a.agg.score);
  for (let i = 0; i < latestRanks.length; i++) {
    latestRanks[i].agg.rank = i + 1;
  }
  aggs.sort((a, b) => a.rank - b.rank);

  return aggs;
}

function teamAggsToSummary(
  currentAggs: TeamCurrentAggs[],
  lastAggs: TeamCurrentAggs[] | undefined,
): TeamSummary[] {
  const summaries: TeamSummary[] = [];
  for (const agg of currentAggs) {
    const lastAgg = lastAggs?.find((lastAgg) => lastAgg.name === agg.name);
    const summary: TeamSummary = {
      name: agg.name,
      currentRank: agg.rank,
      currentScore: agg.score,
      lastRank: lastAgg?.rank ?? agg.rank,
      lastScore: lastAgg?.score ?? agg.score,
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
