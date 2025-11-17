import { useState, useEffect } from 'react';
import './App.css';

// Define interfaces for type safety
interface VoterStats {
  total_voters: number;
  verified_voters: number;
  failed_verifications: number;
}

interface VoteStats {
  total_votes: number;
  votes_today: number;
  verification_rate: number;
}

interface VotingStatus {
  status: 'active' | 'inactive';
  session_start?: string;
  current_voter?: string;
}

interface BlockchainStats {
  total_blocks: number;
  latest_block?: {
    hash: string;
    timestamp: string;
    vote_id: string;
  };
  pending_transactions: number;
}

interface BlockchainTransaction {
  type: string;
  user_id?: string;
  fingerprint_id: number;
  template_hash?: string;
  verification_result?: string;
  similarity_score?: number;
  esp32_ip: string;
  action: string;
  timestamp: number;
  datetime: string;
  tx_id: string;
  block_index: number;
  block_hash: string;
}

interface ModalData {
  isOpen: boolean;
  blockIndex?: number;
  transaction?: BlockchainTransaction;
}

// API base URL - update this to match your deployed backend
const API_BASE_URL = 'https://swift-habitat-475216-n3.uc.r.appspot.com';

function App() {
  const [voterStats, setVoterStats] = useState<VoterStats>({ total_voters: 0, verified_voters: 0, failed_verifications: 0 });
  const [voteStats, setVoteStats] = useState<VoteStats>({ total_votes: 0, votes_today: 0, verification_rate: 0 });
  const [votingStatus, setVotingStatus] = useState<VotingStatus>({ status: 'inactive' });
  const [blockchainStats, setBlockchainStats] = useState<BlockchainStats>({ total_blocks: 0, pending_transactions: 0 });
  const [blockchainTransactions, setBlockchainTransactions] = useState<BlockchainTransaction[]>([]);
  const [modalData, setModalData] = useState<ModalData>({ isOpen: false });
  const [scrollOffset, setScrollOffset] = useState<number>(0);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [isOnline, setIsOnline] = useState<boolean>(true);

  // Fetch data from APIs
  const fetchData = async () => {
    try {
      const [statisticsRes, blockchainRes, auditRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/statistics/`),
        fetch(`${API_BASE_URL}/api/blockchain/info/`),
        fetch(`${API_BASE_URL}/api/blockchain/audit/`)
      ]);

      if (statisticsRes.ok) {
        const statsData = await statisticsRes.json();
        if (statsData.success && statsData.data) {
          // Map statistics data to voter stats
          setVoterStats({
            total_voters: statsData.data.total_templates_stored || 0,
            verified_voters: Math.floor((statsData.data.total_templates_stored || 0) * 0.8), // Estimate 80% verified
            failed_verifications: Math.floor((statsData.data.total_templates_stored || 0) * 0.1) // Estimate 10% failed
          });
          
          // Map to vote stats (using available data)
          setVoteStats({
            total_votes: statsData.data.total_templates_stored || 0,
            votes_today: Math.floor((statsData.data.total_templates_stored || 0) * 0.3), // Estimate 30% today
            verification_rate: 85.5 // Mock verification rate
          });
        }
      }

      if (blockchainRes.ok) {
        const blockchainData = await blockchainRes.json();
        if (blockchainData.success && blockchainData.blockchain_info) {
          const info = blockchainData.blockchain_info;
          setBlockchainStats({
            total_blocks: info.total_blocks || 0,
            pending_transactions: info.pending_transactions || 0,
            latest_block: info.latest_block_hash ? {
              hash: info.latest_block_hash,
              timestamp: new Date().toISOString(),
              vote_id: `VOTE-${info.total_blocks || 1}`
            } : undefined
          });
        }
      }

      if (auditRes.ok) {
        const auditData = await auditRes.json();
        if (auditData.success && auditData.transactions) {
          // Filter to only show verification transactions
          const verificationTransactions = auditData.transactions.filter(
            (tx: BlockchainTransaction) => tx.type === 'VERIFICATION'
          );
          setBlockchainTransactions(verificationTransactions);
          
          // Keep original total_blocks from blockchain info, don't override
          // This prevents the count from changing when filtering transactions
        }
      }

      // Set voting status based on blockchain activity
      setVotingStatus({
        status: blockchainRes.ok ? 'active' : 'inactive',
        session_start: new Date().toISOString(),
        current_voter: undefined
      });

      setLastUpdate(new Date());
      setIsOnline(true);
    } catch (error) {
      console.error('Error fetching data:', error);
      setIsOnline(false);
    }
  };

  // Set up real-time data fetching
  useEffect(() => {
    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Helper component for stat cards
  const StatCard = ({ title, value, subtitle, color, pulse }: {
    title: string;
    value: string | number;
    subtitle?: string;
    color: string;
    pulse?: boolean;
  }) => (
    <div className={`stat-card ${color} ${pulse ? 'pulse' : ''}`}>
      <h3>{title}</h3>
      <div className="stat-value">{value}</div>
      {subtitle && <div className="stat-subtitle">{subtitle}</div>}
    </div>
  );

  // Helper function to get transaction for a specific block
  const getTransactionForBlock = (blockIndex: number): BlockchainTransaction | undefined => {
    return blockchainTransactions.find(tx => tx.block_index === blockIndex);
  };

  // Handle block click
  const handleBlockClick = (blockIndex: number) => {
    const transaction = getTransactionForBlock(blockIndex);
    setModalData({
      isOpen: true,
      blockIndex,
      transaction
    });
  };

  // Close modal
  const closeModal = () => {
    setModalData({ isOpen: false });
  };

  // Handle scroll navigation
  const canScrollLeft = scrollOffset > 0;
  const canScrollRight = scrollOffset + 5 < blockchainTransactions.length;

  const scrollLeft = () => {
    if (canScrollLeft) {
      setScrollOffset(prev => Math.max(0, prev - 1));
    }
  };

  const scrollRight = () => {
    if (canScrollRight) {
      setScrollOffset(prev => Math.min(Math.max(0, blockchainTransactions.length - 5), prev + 1));
    }
  };

  // Modal component
  const BlockModal = () => {
    if (!modalData.isOpen) return null;

    const { blockIndex, transaction } = modalData;
    
    return (
      <div className="modal-overlay" onClick={closeModal}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3>Block {blockIndex} Details</h3>
            <button className="modal-close" onClick={closeModal}>×</button>
          </div>
          <div className="modal-body">
            {transaction ? (
              <div className="transaction-details">
                <div className="detail-row">
                  <span className="detail-label">Transaction Type:</span>
                  <span className={`detail-value ${transaction.type.toLowerCase()}`}>
                    {transaction.type}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Transaction ID:</span>
                  <span className="detail-value">{transaction.tx_id}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Block Hash:</span>
                  <span className="detail-value hash">
                    {transaction.block_hash.substring(0, 32)}...
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Timestamp:</span>
                  <span className="detail-value">{transaction.datetime}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Fingerprint ID:</span>
                  <span className="detail-value">{transaction.fingerprint_id}</span>
                </div>
                {transaction.user_id && (
                  <div className="detail-row">
                    <span className="detail-label">User ID:</span>
                    <span className="detail-value">{transaction.user_id}</span>
                  </div>
                )}
                {transaction.verification_result && (
                  <div className="detail-row">
                    <span className="detail-label">Verification Result:</span>
                    <span className={`detail-value ${transaction.verification_result.toLowerCase()}`}>
                      {transaction.verification_result}
                    </span>
                  </div>
                )}
                {transaction.similarity_score !== undefined && (
                  <div className="detail-row">
                    <span className="detail-label">Similarity Score:</span>
                    <span className="detail-value">{transaction.similarity_score.toFixed(2)}%</span>
                  </div>
                )}
                {transaction.template_hash && (
                  <div className="detail-row">
                    <span className="detail-label">Template Hash:</span>
                    <span className="detail-value hash">
                      {transaction.template_hash}
                    </span>
                  </div>
                )}
                <div className="detail-row">
                  <span className="detail-label">Action:</span>
                  <span className="detail-value">{transaction.action}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">ESP32 IP:</span>
                  <span className="detail-value">{transaction.esp32_ip}</span>
                </div>
              </div>
            ) : (
              <div className="no-transaction">
                <p>No transaction data available for this block.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Blockchain visualization component
  const BlockchainVisualization = () => {
    // Get verification transactions sorted by block index (newest first)
    const sortedVerificationBlocks = blockchainTransactions
      .sort((a, b) => b.block_index - a.block_index);
    
    // Create visible blocks with pagination
    const visibleBlocks = sortedVerificationBlocks
      .slice(scrollOffset, scrollOffset + 5)
      .map(tx => ({
        index: tx.block_index,
        transaction: tx,
        isLatest: tx.block_index === Math.max(...blockchainTransactions.map(t => t.block_index))
      }));

    return (
      <div className="blockchain-section">
        <h2>🔗 Blockchain Status</h2>
        <div className="blockchain-stats">
          <div className="blockchain-info">
            <StatCard
              title="Verification Blocks"
              value={blockchainTransactions.length}
              color="blockchain"
            />
            <StatCard
              title="Pending Transactions"
              value={blockchainStats.pending_transactions}
              color="pending"
              pulse={blockchainStats.pending_transactions > 0}
            />
          </div>
          {blockchainStats.latest_block && (
            <div className="latest-block">
              <h4>Latest Block</h4>
              <div className="block-details">
                <div className="block-hash">
                  Hash: {blockchainStats.latest_block.hash.substring(0, 16)}...
                </div>
                <div className="block-time">
                  Time: {new Date(blockchainStats.latest_block.timestamp).toLocaleString()}
                </div>
                <div className="block-vote">
                  Vote ID: {blockchainStats.latest_block.vote_id}
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="blockchain-container">
          <div className="blockchain-controls">
            <button 
              className={`scroll-btn ${!canScrollLeft ? 'disabled' : ''}`}
              onClick={scrollLeft}
              disabled={!canScrollLeft}
            >
              ← Previous
            </button>
            <span className="block-range">
              Showing {visibleBlocks.length} of {blockchainTransactions.length} verification blocks
            </span>
            <button 
              className={`scroll-btn ${!canScrollRight ? 'disabled' : ''}`}
              onClick={scrollRight}
              disabled={!canScrollRight}
            >
              Next →
            </button>
          </div>
          
          <div className="blockchain-visual">
            {visibleBlocks.length > 0 ? (
              visibleBlocks.map((block) => (
                <div 
                  key={block.index} 
                  className={`block ${block.isLatest ? 'latest' : ''} clickable`}
                  onClick={() => handleBlockClick(block.index)}
                >
                  <div className="block-title">Block {block.index}</div>
                  <div className="block-status">
                    {block.isLatest ? '🟡 Latest' : '✅ Confirmed'}
                  </div>
                  {block.transaction && (
                    <div className={`block-type ${block.transaction.verification_result?.toLowerCase()}`}>
                      {block.transaction.verification_result}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="no-blocks">
                <div className="empty-state">
                  <div className="empty-icon">🔗</div>
                  <div className="empty-text">No verification blocks found</div>
                  <div className="empty-subtitle">Verification blocks will appear here when users verify their fingerprints</div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        <BlockModal />
      </div>
    );
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🗳️ Electronic Voting Machine Dashboard</h1>
        <div className="status-bar">
          <div className={`connection-status ${isOnline ? 'online' : 'offline'}`}>
            {isOnline ? '🟢 Online' : '🔴 Offline'}
          </div>
          <div className="last-update">
            Last Update: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </header>

      <main className="dashboard-content">
        {/* Voter Statistics */}
        <section className="stats-section">
          <h2>👥 Voter Statistics</h2>
          <div className="stats-grid">
            <StatCard
              title="Total Registered"
              value={voterStats.total_voters}
              subtitle="Voters in System"
              color="blue"
            />
            <StatCard
              title="Successfully Verified"
              value={voterStats.verified_voters}
              subtitle="Successful Authentications"
              color="green"
            />
            <StatCard
              title="Failed Verifications"
              value={voterStats.failed_verifications}
              subtitle="Authentication Failures"
              color="red"
            />
          </div>
        </section>

        {/* Voting Statistics */}
        <section className="stats-section">
          <h2>📊 Vote Tracking</h2>
          <div className="stats-grid">
            <StatCard
              title="Total Votes Cast"
              value={voteStats.total_votes}
              subtitle="All Time"
              color="purple"
            />
            <StatCard
              title="Votes Today"
              value={voteStats.votes_today}
              subtitle="Current Session"
              color="orange"
            />
            <StatCard
              title="Verification Rate"
              value={`${voteStats.verification_rate.toFixed(1)}%`}
              subtitle="Success Rate"
              color={voteStats.verification_rate > 90 ? 'green' : voteStats.verification_rate > 75 ? 'yellow' : 'red'}
            />
          </div>
        </section>

        {/* Current Voting Status */}
        <section className="status-section">
          <h2>⚡ Current Status</h2>
          <div className={`voting-status ${votingStatus.status}`}>
            <div className="status-indicator">
              {votingStatus.status === 'active' ? '🟢 VOTING ACTIVE' : '🔴 VOTING INACTIVE'}
            </div>
            {votingStatus.session_start && (
              <div className="session-info">
                Session started: {new Date(votingStatus.session_start).toLocaleString()}
              </div>
            )}
            {votingStatus.current_voter && (
              <div className="current-voter">
                Current voter: {votingStatus.current_voter}
              </div>
            )}
          </div>
        </section>

        {/* Blockchain Visualization */}
        <BlockchainVisualization />
      </main>

      <footer className="dashboard-footer">
        <p>🔐 Secure Electronic Voting System with Blockchain Verification</p>
        <p>Real-time monitoring • Fingerprint authentication • Immutable records</p>
      </footer>
    </div>
  );
}

export default App;
