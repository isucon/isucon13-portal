import React from 'react';
import { Link } from 'react-router-dom';

export default function IndexPage(): React.ReactElement {
  return (
    <div>
      <h1>Broadcast utils</h1>
      <ul>
        <li>
          <Link to="/leader">Leader boead</Link>
        </li>
      </ul>
    </div>
  );
}
