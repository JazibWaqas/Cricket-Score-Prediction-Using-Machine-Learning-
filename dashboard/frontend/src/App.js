import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import TeamSelector from './components/TeamSelector';
import MatchScenario from './components/MatchScenario';
import PredictionDisplay from './components/PredictionDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import MatchContextDisplay from './components/MatchContextDisplay';
import TeamFormationDisplay from './components/TeamFormationDisplay';
import api from './utils/api';

function App() {
  const [teams, setTeams] = useState([]);
  const [players, setPlayers] = useState([]);
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  // Team selection - matches root frontend structure
  const [teamA, setTeamA] = useState({
    team_id: null,
    team_name: '',
    players: []
  });

  const [teamB, setTeamB] = useState({
    team_id: null,
    team_name: '',
    players: []
  });

  // Match scenario
  const [matchScenario, setMatchScenario] = useState({
    venue: '',
    venue_avg_score: 250,
    current_score: '',
    wickets_fallen: '',
    overs: '',
    runs_last_10: '',
    batsman_1: '',
    batsman_2: ''
  });
  // Show players from any country when true (What-if scenario)
  const [whatIfAllPlayers, setWhatIfAllPlayers] = useState(false);

  // Model selection
  // selectedModel stores the canonical identifier (value), e.g. 'xgboost' or 'random_forest'
  const [selectedModel, setSelectedModel] = useState('xgboost');
  // Fallback list of models as {label, value}
  const [availableModels, setAvailableModels] = useState([
    { label: 'XGBoost', value: 'xgboost' },
    { label: 'Random Forest', value: 'random_forest' }
  ]);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load essential data first
        const [teamsRes, playersRes, venuesRes] = await Promise.all([
          api.getTeams(),
          api.getPlayers(),
          api.getVenues()
        ]);

        setTeams(teamsRes.data.teams);
        setPlayers(playersRes.data.players);
        setVenues(venuesRes.data.venues);

        // Load models separately (non-critical, has fallback)
        try {
          const modelsRes = await api.getModels();
          if (modelsRes.data.models) {
            // modelsRes.data.models expected format: [{label, value}, ...] or string list
            const remoteModels = modelsRes.data.models.map(m => {
              if (typeof m === 'string') {
                return { label: m, value: m.toLowerCase().replace(/\s+/g, '_') };
              }
              return m;
            });

            // Merge remote models with client fallback so commonly expected models
            // like Random Forest are visible even if backend doesn't list them.
            const fallback = [
              { label: 'XGBoost', value: 'xgboost' },
              { label: 'Random Forest', value: 'random_forest' }
            ];

            // Build map by value to preserve remote ordering but include fallbacks
            const map = new Map();
            remoteModels.forEach(m => map.set(m.value, m));
            fallback.forEach(m => { if (!map.has(m.value)) map.set(m.value, m); });

            const merged = Array.from(map.values());
            setAvailableModels(merged);
            setSelectedModel(modelsRes.data.default || (merged[0] && merged[0].value));
          }
        } catch (modelErr) {
          console.warn('Could not load models, using default fallback:', modelErr);
          // Keep client-side fallback
        }

        setLoading(false);
      } catch (err) {
        setError('Failed to load data. Make sure backend is running on port 5002');
        console.error('Load error:', err);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Handle team selection
  const handleTeamSelect = (teamType, teamId, teamName) => {
    if (teamType === 'A') {
      setTeamA({ team_id: teamId, team_name: teamName, players: [] });
    } else {
      setTeamB({ team_id: teamId, team_name: teamName, players: [] });
    }
  };

  // Handle player selection
  const handlePlayerSelect = (teamType, playerId, playerName, playerCountry) => {
    const player = { id: playerId, name: playerName, country: playerCountry };

    if (teamType === 'A') {
      if (teamA.players.length < 11) {
        setTeamA(prev => ({ ...prev, players: [...prev.players, player] }));
      }
    } else {
      if (teamB.players.length < 11) {
        setTeamB(prev => ({ ...prev, players: [...prev.players, player] }));
      }
    }
  };

  // Handle player removal
  const handleRemovePlayer = (teamType, playerId) => {
    if (teamType === 'A') {
      setTeamA(prev => ({ ...prev, players: prev.players.filter(p => p.id !== playerId) }));
    } else {
      setTeamB(prev => ({ ...prev, players: prev.players.filter(p => p.id !== playerId) }));
    }
  };

  // Handle prediction
  const handlePredict = async () => {
    console.log('Prediction request - Team A players:', teamA.players.length);
    console.log('Prediction request - Team B players:', teamB.players.length);
    console.log('Prediction request - Venue:', matchScenario.venue);

    if (teamA.players.length < 11) {
      setError('Please select 11 players for Team A (Batting Team)');
      return;
    }

    if (teamB.players.length < 11) {
      setError('Please select 11 players for Team B (Opposition)');
      return;
    }

    if (!matchScenario.venue) {
      setError('Please select a venue');
      return;
    }

    setPredicting(true);
    setError(null);

    try {
      const current_score = Number(matchScenario.current_score) || 0;
      const wickets_fallen = Number(matchScenario.wickets_fallen) || 0;
      const oversNumber = Number(matchScenario.overs) || 0;
      const runs_last_10 = Number(matchScenario.runs_last_10) || 0;
      const balls_bowled = oversNumber * 6;

      const requestData = {
        batting_team_players: teamA.players.map(p => p.name),
        bowling_team_players: teamB.players.map(p => p.name),
        venue: matchScenario.venue,
        venue_avg_score: matchScenario.venue_avg_score,
        current_score: current_score,
        wickets_fallen: wickets_fallen,
        balls_bowled: balls_bowled,
        runs_last_10_overs: runs_last_10,
        batsman_1: matchScenario.batsman_1,
        batsman_2: matchScenario.batsman_2,
        model: selectedModel  // Include selected model
      };

      console.log('Sending prediction request:', requestData);

      const response = await api.predict(requestData);

      setPrediction(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed. Check console for details.');
      console.error('Prediction error:', err);
    } finally {
      setPredicting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 bg-red-900/20 border border-red-500/50 rounded-lg p-4 text-red-400"
          >
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 text-sm underline"
            >
              Dismiss
            </button>
          </motion.div>
        )}

        <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          {/* Model Selector */}
          <div className="flex items-center gap-6">
            <div>
              <div className="text-lg font-semibold text-cricket-green">Model</div>
              <div className="text-xs text-dark-muted">Choose model for prediction</div>
            </div>

            <div className="flex items-center gap-3">
              {availableModels.map(m => (
                <button
                  key={m.value}
                  onClick={() => setSelectedModel(m.value)}
                  className={
                    `px-4 py-2 border rounded-lg text-sm transition-colors focus:outline-none ` +
                    (selectedModel === m.value
                      ? 'bg-cricket-green text-white border-cricket-green'
                      : 'bg-black text-white border-gray-700 hover:border-cricket-green')
                  }
                  aria-pressed={selectedModel === m.value}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>

          {/* What-if checkbox */}
          <label className="inline-flex items-center gap-3 text-sm text-dark-muted">
            <input
              type="checkbox"
              checked={whatIfAllPlayers}
              onChange={(e) => setWhatIfAllPlayers(e.target.checked)}
              className="h-4 w-4"
            />
            <span>What-if scenario: show players from all countries</span>
          </label>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Team A - Batting Team */}
          <TeamSelector
            teamType="A"
            team={teamA}
            teams={teams}
            players={players}
            whatIfAllPlayers={whatIfAllPlayers}
            onTeamSelect={handleTeamSelect}
            onPlayerSelect={handlePlayerSelect}
            onRemovePlayer={handleRemovePlayer}
          />

          {/* Team B - Opposition */}
          <TeamSelector
            teamType="B"
            team={teamB}
            teams={teams}
            players={players}
            whatIfAllPlayers={whatIfAllPlayers}
            onTeamSelect={handleTeamSelect}
            onPlayerSelect={handlePlayerSelect}
            onRemovePlayer={handleRemovePlayer}
          />
        </div>

        {/* Team Formation Displays */}
        {(teamA.players.length > 0 || teamB.players.length > 0) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {teamA.players.length > 0 && (
              <TeamFormationDisplay
                team={teamA}
                teamType="A"
                players={players}
              />
            )}
            {teamB.players.length > 0 && (
              <TeamFormationDisplay
                team={teamB}
                teamType="B"
                players={players}
              />
            )}
          </div>
        )}

        {/* Match Scenario */}
        <MatchScenario
          scenario={matchScenario}
          onChange={setMatchScenario}
          venues={venues}
          battingPlayers={teamA.players}
        />

        {/* Match Context Display */}
        <MatchContextDisplay
          teamA={teamA}
          teamB={teamB}
          scenario={matchScenario}
          venues={venues}
        />

        {/* Predict Button */}
        <div className="text-center my-8">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handlePredict}
            disabled={predicting}
            className="cricket-button text-xl px-12 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {predicting ? 'Predicting...' : '🏏 Predict Final Score'}
          </motion.button>
        </div>

        {/* Prediction Results */}
        {prediction && (
          <PredictionDisplay prediction={prediction} scenario={matchScenario} />
        )}
      </main>
    </div>
  );
}

export default App;
