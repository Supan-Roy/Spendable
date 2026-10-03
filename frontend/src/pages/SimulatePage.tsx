import React, { useState, useRef, useEffect } from 'react';
import { postSimulateApi, postChatApi } from '../api/spendable';
import type { ScenarioType, ScenarioResult, ChatMessage } from '../api/types';
import { formatCurrency, formatDateTime, getLiquidityBadgeConfig } from '../utils/formatters';
import { Sliders, ArrowRight, RotateCcw, AlertTriangle, Shield, Bot, Sparkles, Send, MessageSquare, Zap } from 'lucide-react';

export const SimulatePage: React.FC = () => {
  const [scenarioType, setScenarioType] = useState<ScenarioType>('ONE_TIME_EXPENSE');
  const [amount, setAmount] = useState<string>('5000');
  const [changePercentage, setChangePercentage] = useState<string>('10');
  const [delayDays, setDelayDays] = useState<string>('7');
  const [description, setDescription] = useState<string>('');

  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Spendable AI Chat States
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I am **Spendable AI**, your personal financial liquidity assistant. Ask me anything about your current spendable capacity, 30-day balance trajectory, recurring commitments, or what-if scenario simulations!',
    },
  ]);
  const [inputQuery, setInputQuery] = useState<string>('');
  const [isChatSending, setIsChatSending] = useState<boolean>(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, isChatSending]);

  const handleSimulate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const numAmt = parseFloat(amount) || 0;
      const numPct = parseFloat(changePercentage) || 0;
      const numDays = parseInt(delayDays, 10) || 0;

      const res = await postSimulateApi({
        scenario_type: scenarioType,
        amount: scenarioType === 'ONE_TIME_EXPENSE' || scenarioType === 'ONE_TIME_INCOME' || scenarioType === 'RECURRING_EXPENSE' ? numAmt : undefined,
        change_percentage: scenarioType === 'INCOME_CHANGE' ? numPct : undefined,
        delay_days: scenarioType === 'INCOME_DELAY' ? numDays : undefined,
        description: description.trim() || undefined,
      });

      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to simulate scenario.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setAmount('5000');
    setDescription('');
  };

  const handleSendChatMessage = async (overridePrompt?: string) => {
    const messageToSend = (overridePrompt || inputQuery).trim();
    if (!messageToSend || isChatSending) return;

    const newHistory: ChatMessage[] = [
      ...chatMessages,
      { role: 'user', content: messageToSend },
    ];

    setChatMessages(newHistory);
    if (!overridePrompt) setInputQuery('');
    setIsChatSending(true);

    try {
      const res = await postChatApi(messageToSend, chatMessages, result || undefined);
      setChatMessages([
        ...newHistory,
        { role: 'assistant', content: res.reply },
      ]);
    } catch (err: any) {
      setChatMessages([
        ...newHistory,
        {
          role: 'assistant',
          content: 'I am **Spendable AI**. I encountered a temporary connection issue fetching live account metrics, but I am still online to help you analyze your finances! Please try your question again.',
        },
      ]);
    } finally {
      setIsChatSending(false);
    }
  };

  const samplePrompts = [
    'Can I afford a ৳15,000 purchase right now?',
    'What are my highest upcoming recurring bills?',
    'How does my 30-day liquidity risk look?',
    'What happens if my income is delayed by 10 days?',
  ];

  const baseBadge = result ? getLiquidityBadgeConfig(result.base_liquidity_state) : null;
  const scenarioBadge = result ? getLiquidityBadgeConfig(result.scenario_liquidity_state) : null;

  return (
    <div className="tab-pane">
      <div className="page-header">
        <h2>What-If Scenario Simulator</h2>
        <p className="subtitle">Simulate financial changes and ask Spendable AI anything about your money runway.</p>
      </div>

      <div className="simulate-layout-grid">
        {/* Left Form Panel */}
        <div className="simulate-form-card">
          <div className="form-card-header">
            <Sliders size={20} color="#00e5a3" />
            <h3>Choose Scenario</h3>
          </div>

          <form onSubmit={handleSimulate}>
            <div className="form-group">
              <label>Scenario Type</label>
              <select
                value={scenarioType}
                onChange={(e) => {
                  setScenarioType(e.target.value as ScenarioType);
                  setResult(null);
                }}
                disabled={isLoading}
              >
                <option value="ONE_TIME_EXPENSE">Spend money (One-time expense)</option>
                <option value="ONE_TIME_INCOME">Receive money (One-time inflow)</option>
                <option value="RECURRING_EXPENSE">Add commitment (Monthly bill/rent)</option>
                <option value="INCOME_CHANGE">Income change (%)</option>
                <option value="INCOME_DELAY">Delay income (Days)</option>
              </select>
            </div>

            {(scenarioType === 'ONE_TIME_EXPENSE' ||
              scenarioType === 'ONE_TIME_INCOME' ||
              scenarioType === 'RECURRING_EXPENSE') && (
              <div className="form-group">
                <label>Amount (৳)</label>
                <div className="input-currency-wrapper">
                  <span className="input-symbol">৳</span>
                  <input
                    type="number"
                    min="0.01"
                    step="any"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="5000"
                    disabled={isLoading}
                  />
                </div>
              </div>
            )}

            {scenarioType === 'INCOME_CHANGE' && (
              <div className="form-group">
                <label>Income Change (%)</label>
                <input
                  type="number"
                  step="any"
                  value={changePercentage}
                  onChange={(e) => setChangePercentage(e.target.value)}
                  placeholder="-10 or +15"
                  disabled={isLoading}
                />
              </div>
            )}

            {scenarioType === 'INCOME_DELAY' && (
              <div className="form-group">
                <label>Delay (Days)</label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={delayDays}
                  onChange={(e) => setDelayDays(e.target.value)}
                  placeholder="7"
                  disabled={isLoading}
                />
              </div>
            )}

            <div className="form-group">
              <label>Description (Optional)</label>
              <input
                type="text"
                placeholder="e.g. New smartphone purchase"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isLoading}
              />
            </div>

            <div className="form-action-group">
              <button type="submit" className="primary-btn full-width" disabled={isLoading}>
                {isLoading ? 'Simulating...' : 'Simulate Scenario'}
              </button>
              {result && (
                <button type="button" className="secondary-btn" onClick={handleReset} disabled={isLoading}>
                  <RotateCcw size={14} />
                  <span>Reset</span>
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Right Output Panel */}
        <div className="simulate-output-container">
          {error && (
            <div className="auth-error-banner">
              <AlertTriangle size={16} />
              <span>{error}</span>
            </div>
          )}

          {!result ? (
            <div className="empty-state-card simulate-placeholder-card">
              <Sliders size={40} className="empty-icon" />
              <h3>Ready to Simulate</h3>
              <p>
                Enter a hypothetical expense or financial change on the left and click <strong>Simulate Scenario</strong> to see how your safe spending runway changes.
              </p>
            </div>
          ) : (
            <div className="scenario-results-card">
              <div className="results-header">
                <div>
                  <h3>Scenario Impact Result</h3>
                  {result.snapshot_time && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      Simulated at {formatDateTime(result.snapshot_time)}
                    </div>
                  )}
                </div>
                {result.state_changed && (
                  <span className="state-changed-tag">State Changed</span>
                )}
              </div>

              {/* Before vs After Visual Comparison */}
              <div className="before-after-grid">
                <div className="comparison-box before-box">
                  <span className="box-title">BEFORE (BASE)</span>
                  <span className="box-amount">{formatCurrency(result.base_spendable)}</span>
                  {baseBadge && (
                    <span className="mini-status-badge" style={{ color: baseBadge.color }}>
                      {baseBadge.label}
                    </span>
                  )}
                </div>

                <div className="comparison-arrow">
                  <ArrowRight size={24} color="#00e5a3" />
                  <span className={`delta-tag ${result.spendable_delta < 0 ? 'negative' : 'positive'}`}>
                    {result.spendable_delta >= 0 ? '+' : ''}
                    {formatCurrency(result.spendable_delta)}
                  </span>
                </div>

                <div className="comparison-box after-box">
                  <span className="box-title">AFTER (SCENARIO)</span>
                  <span className="box-amount scenario-highlight">{formatCurrency(result.scenario_spendable)}</span>
                  {scenarioBadge && (
                    <span className="mini-status-badge" style={{ color: scenarioBadge.color }}>
                      {scenarioBadge.label}
                    </span>
                  )}
                </div>
              </div>

              {/* Scenario Explanation */}
              {result.explanation && (
                <div className="scenario-explanation-box">
                  <div className="explanation-header">
                    <Shield size={16} color="#00e5a3" />
                    <h4>Impact Analysis</h4>
                  </div>
                  <p>{result.explanation}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ==========================================================================
         SPENDABLE AI ASSISTANT CHAT INTERFACE
         ========================================================================== */}
      <div className="spendable-ai-chat-card">
        <div className="chat-header-bar">
          <div className="chat-title-group">
            <div className="chat-ai-icon-badge">
              <Bot size={22} />
            </div>
            <div>
              <h3>
                Spendable AI
                <Sparkles size={16} color="#00e5a3" />
              </h3>
              <p>Personal Financial Intelligence & Context-Aware Assistant</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            {result && (
              <div className="scenario-context-chip">
                <Zap size={14} />
                <span>Simulated Scenario Context Attached</span>
              </div>
            )}
            <div className="chat-live-badge">
              <span className="chat-status-dot"></span>
              <span>Live Account Data Ingested</span>
            </div>
          </div>
        </div>

        {/* Quick Prompt Recommendation Pills */}
        <div className="chat-prompts-container">
          {samplePrompts.map((promptText, idx) => (
            <button
              key={idx}
              className="chat-prompt-pill"
              onClick={() => handleSendChatMessage(promptText)}
              disabled={isChatSending}
            >
              <MessageSquare size={13} color="#00e5a3" />
              <span>{promptText}</span>
            </button>
          ))}
        </div>

        {/* Messages Stream */}
        <div className="chat-messages-container">
          {chatMessages.map((msg, index) => (
            <div
              key={index}
              className={`chat-message-row ${msg.role === 'user' ? 'user-row' : 'ai-row'}`}
            >
              <div className={`chat-avatar ${msg.role === 'user' ? 'user-avatar' : 'ai-avatar'}`}>
                {msg.role === 'user' ? 'YOU' : <Bot size={18} />}
              </div>

              <div className={`chat-bubble ${msg.role === 'user' ? 'user-bubble' : 'ai-bubble'}`}>
                {msg.role === 'assistant' && (
                  <div className="chat-ai-name-tag">
                    <Sparkles size={12} />
                    <span>Spendable AI</span>
                  </div>
                )}
                <div>{msg.content}</div>
              </div>
            </div>
          ))}

          {isChatSending && (
            <div className="chat-message-row ai-row">
              <div className="chat-avatar ai-avatar">
                <Bot size={18} />
              </div>
              <div className="chat-bubble ai-bubble" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#00e5a3' }}>
                <Sparkles size={16} className="animate-spin" />
                <span>Spendable AI is analyzing your transactions & liquidity context...</span>
              </div>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        {/* Input Bar */}
        <form
          className="chat-input-wrapper"
          onSubmit={(e) => {
            e.preventDefault();
            handleSendChatMessage();
          }}
        >
          <input
            type="text"
            className="chat-text-input"
            placeholder="Ask Spendable AI about your spending runway, recurring bills, or safe purchase limits..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={isChatSending}
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={!inputQuery.trim() || isChatSending}
          >
            <span>Send</span>
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
};
