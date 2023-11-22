import React from 'react';
import { Link } from 'react-router-dom';

export default function IndexPage(): React.ReactElement {
  return (
    <div>
      <h1>Broadcast utils</h1>
      <ul>
        <li>
          <Link to="/leader">Leader boead</Link>
          <ul>
            <li>
              <Link to="/leader?limit=25">limit 25</Link>
            </li>
            <li>
              <Link to="/leader?bottom=1">bottom</Link>
            </li>
            <li>
              <Link to="/leader?limit=10&bottom=1">limit 10 & bottom</Link>
            </li>
          </ul>
        </li>
        <li>
          <Link to="/changes">Changes</Link>
          <ul>
            <li>
              <Link to="/changes?limit=25">limit 25</Link>
            </li>
            <li>
              <Link to="/changes?bottom=1">bottom</Link>
            </li>
            <li>
              <Link to="/changes?limit=10&bottom=1">limit 10 & bottom</Link>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  );
}
