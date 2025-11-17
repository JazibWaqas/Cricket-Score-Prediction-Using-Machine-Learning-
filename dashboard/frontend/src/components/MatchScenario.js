import React from 'react';
import { motion } from 'framer-motion';

const MatchScenario = ({ scenario, onChange, venues, battingPlayers }) => {
  const handleChange = (field, value) => {
    onChange({ ...scenario, [field]: value });
  };
  
  const handleVenueChange = (venueName) => {
    const selectedVenue = venues.find(v => v.venue_name === venueName);
    onChange({
      ...scenario,
      venue: venueName,
      venue_avg_score: selectedVenue && selectedVenue.avg_score ? selectedVenue.avg_score : 250
    });
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="cricket-card"
    >
      <h2 className="text-2xl font-bold text-cricket-green mb-6">Match Scenario</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Venue */}
        <div>
          <label className="block text-dark-muted mb-2">Venue</label>
          <select
            value={scenario.venue}
            onChange={(e) => handleVenueChange(e.target.value)}
            className="cricket-select w-full"
          >
            <option value="">Select venue...</option>
            {venues.map(venue => (
              <option key={venue.venue_name} value={venue.venue_name}>
                {venue.venue_name} {venue.avg_score ? `(Avg: ${venue.avg_score.toFixed(0)})` : ''}
              </option>
            ))}
          </select>
        </div>
        
        {/* Current Score */}
        <div>
          <label className="block text-dark-muted mb-2">Current Score</label>
            <input
              type="number"
              value={scenario.current_score}
              onChange={(e) => {
                const v = e.target.value;
                handleChange('current_score', v === '' ? '' : parseInt(v, 10));
              }}
              className="cricket-input w-full"
              min="0"
              max="500"
            />
        </div>
        
        {/* Wickets */}
        <div>
          <label className="block text-dark-muted mb-2">Wickets Fallen</label>
          <input
            type="number"
            value={scenario.wickets_fallen}
            onChange={(e) => {
              const v = e.target.value;
              handleChange('wickets_fallen', v === '' ? '' : parseInt(v, 10));
            }}
            className="cricket-input w-full"
            min="0"
            max="10"
          />
        </div>
        
        {/* Overs */}
        <div>
          <label className="block text-dark-muted mb-2">Overs Completed</label>
          <input
            type="number"
            value={scenario.overs}
            onChange={(e) => {
              const v = e.target.value;
              handleChange('overs', v === '' ? '' : parseInt(v, 10));
            }}
            className="cricket-input w-full"
            min="0"
            max="50"
            step="1"
          />
        </div>
        
        {/* Runs in Last 10 Overs */}
        <div>
          <label className="block text-dark-muted mb-2">Runs in Last 10 Overs</label>
          <input
            type="number"
            value={scenario.runs_last_10}
            onChange={(e) => {
              const v = e.target.value;
              handleChange('runs_last_10', v === '' ? '' : parseInt(v, 10));
            }}
            className="cricket-input w-full"
            min="0"
            max="200"
          />
        </div>
        
        {/* Current Batsman 1 */}
        <div>
          <label className="block text-dark-muted mb-2">Current Batsman 1 (optional)</label>
          <select
            value={scenario.batsman_1}
            onChange={(e) => handleChange('batsman_1', e.target.value)}
            className="cricket-select w-full"
          >
            <option value="">None</option>
            {battingPlayers.length > 0 && battingPlayers.map(player => (
              <option key={player.id} value={player.name}>
                {player.name}
              </option>
            ))}
          </select>
        </div>
        
        {/* Current Batsman 2 */}
        <div>
          <label className="block text-dark-muted mb-2">Current Batsman 2 (optional)</label>
          <select
            value={scenario.batsman_2}
            onChange={(e) => handleChange('batsman_2', e.target.value)}
            className="cricket-select w-full"
          >
            <option value="">None</option>
            {battingPlayers.length > 0 && battingPlayers.map(player => (
              <option key={player.id} value={player.name}>
                {player.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Quick Scenarios removed per request */}
    </motion.div>
  );
};

export default MatchScenario;

