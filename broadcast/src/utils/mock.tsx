import { GraphData, GraphDataResponse, GraphDataset, Ranking } from './types';

const teams = new Array(30).fill(undefined).map((_, i) => ({
  name: `Team ${i}`.repeat(i % 7 === 0 ? 15 : 1),
}));

export function fetchMockGraph(): () => Promise<GraphDataResponse> {
  let count = 0;

  return () =>
    new Promise((resolve) => {
      count++;
      const datasets: GraphDataset[] = teams.map((team, teamIndex) => {
        const random = new Random(teamIndex);

        const data: GraphData[] = [];
        let lastScore = 0;
        for (let i = 0; i < count; i++) {
          const score =
            lastScore === 0 || random.nextInt(0, 10) > 7
              ? random.nextInt(500, 1000 + i * 100)
              : lastScore;
          lastScore = score;
          data.push({
            x: new Date(
              new Date('2023-11-25 09:00:00').valueOf() + i * 5000,
            ).toISOString(),
            y: score,
          });
        }

        return {
          label: team.name,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgb(255, 99, 132)',
          hoverBackgroundColor: 'rgba(255, 99, 132, 0.4)',
          hoverBorderColor: 'rgb(255, 99, 132)',
          pointHoverBorderWidth: 2,
          lineTension: 0,
          borderWidth: 1,
          pointRadius: 0,
          fill: false,
          spanGaps: false,
          data,
        };
      });

      const ranks = datasets
        .map((dataset, index) => ({ index, dataset }))
        .sort(
          (a, b) =>
            b.dataset.data[b.dataset.data.length - 1].y -
            a.dataset.data[a.dataset.data.length - 1].y,
        );

      const ranking: Ranking[] = teams.map((team, teamIndex) => {
        const score =
          datasets[teamIndex].data[datasets[teamIndex].data.length - 1].y;
        const rank = ranks.findIndex((r) => r.index === teamIndex) + 1;

        return {
          team: {
            name: team.name,
            id: teamIndex,
            has_student: teamIndex % 5 === 0,
            is_guest: teamIndex % 6 === 0,
          },
          latest_score: score,
          rank,
        } satisfies Ranking;
      });

      const response: GraphDataResponse = {
        graph_datasets: datasets,
        graph_min: '2023-11-25 09:00:00',
        graph_max: '2023-11-25 18:00:00',
        ranking,
      };

      return setTimeout(() => {
        resolve(response);
      }, 200);
    });
}

class Random {
  private x = 123456789;
  private y = 362436069;
  private z = 521288629;
  private w: number;

  constructor(seed = 1) {
    this.w = seed;
  }
  // XorShift
  next() {
    const t = this.x ^ (this.x << 11);
    this.x = this.y;
    this.y = this.z;
    this.z = this.w;
    return (this.w = this.w ^ (this.w >>> 19) ^ (t ^ (t >>> 8)));
  }
  nextInt(min: number, max: number) {
    const r = Math.abs(this.next());
    return min + (r % (max + 1 - min));
  }
}
