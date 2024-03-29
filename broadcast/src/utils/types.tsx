export interface GraphDataset {
  label: string;
  backgroundColor: string;
  borderColor: string;
  hoverBackgroundColor: string;
  hoverBorderColor: string;
  pointHoverBorderWidth: number;
  lineTension: number;
  borderWidth: number;
  pointRadius: number;
  fill: boolean;
  spanGaps: boolean;
  data: GraphData[];
}

export interface GraphData {
  x: string; // date format: YYYY-MM-DD hh:mm:ss
  y: number; // integer points
}

export interface GraphDataResponse {
  graph_datasets: GraphDataset[];
  graph_min: string;
  graph_max: string;
  ranking: Ranking[];
}

export interface Ranking {
  team: Team;
  latest_score: number;
  rank: number;
}

export interface Team {
  id: number;
  name: string;
  has_student: boolean;
  is_guest: boolean;
}
