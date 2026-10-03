import React, { useState, useRef, useEffect } from 'react';
import { postSimulateApi, postChatApi } from '../api/spendable';
import type { ScenarioType, ScenarioResult, ChatMessage } from '../api/types';
import { formatCurrency, getLiquidityBadgeConfig } from '../utils/formatters';
import { Sliders, ArrowRight, RotateCcw, AlertTriangle, Shield, Bot, Sparkles, Send, MessageSquare, Zap, ChevronDown, ChevronUp } from 'lucide-react';

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
  const [isAiOpen, setIsAiOpen] = useState<boolean>(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I am **Spendable AI**, your personal financial liquidity assistant. Ask me anything about your current spendable capacity, 30-day balance trajectory, recurring commitments, or what-if scenario simulations!',
    },
  ]);
  const [inputQuery, setInputQuery] = useState<string>('');
  const [isChatSending, setIsChatSending] = useState<boolean>(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);
  const isInitialMount = useRef<boolean>(true);

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    if (isAiOpen) {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, isChatSending, isAiOpen]);

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

    if (!isAiOpen) setIsAiOpen(true);

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

  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    return (
      <div className="formatted-ai-text">
        {lines.map((line, lIdx) => {
          let trimmed = line.trim();
          if (!trimmed) return <div key={lIdx} style={{ height: '0.4rem' }} />;

          const isBullet = trimmed.startsWith('- ') || trimmed.startsWith('* ');
          if (isBullet) {
            trimmed = trimmed.substring(2).trim();
          }

          const parts = trimmed.split(/(\*\*.*?\*\*|\*.*?\*)/g);
          const parsedElements = parts.map((part, pIdx) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
              return <strong key={pIdx} style={{ color: '#ffffff', fontWeight: 700 }}>{part.slice(2, -2)}</strong>;
            }
            if (part.startsWith('*') && part.endsWith('*') && part.length >= 2) {
              return <em key={pIdx} style={{ fontStyle: 'italic', color: '#cbd5e1' }}>{part.slice(1, -1)}</em>;
            }
            return part;
          });

          if (isBullet) {
            return (
              <div key={lIdx} style={{ display: 'flex', gap: '0.4rem', alignItems: 'flex-start', margin: '0.25rem 0' }}>
                <span style={{ color: '#00e5a3', fontSize: '0.9rem', lineHeight: '1.4' }}>•</span>
                <span style={{ flex: 1 }}>{parsedElements}</span>
              </div>
            );
          }

          return <p key={lIdx} style={{ margin: '0 0 0.35rem 0' }}>{parsedElements}</p>;
        })}
      </div>
    );
  };

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
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    {result.scenario_description || result.description || 'Hypothetical financial simulation result'}
                  </div>
                </div>
                {result.base_liquidity_state !== result.scenario_liquidity_state && (
                  <span className="state-changed-tag">State Changed: {result.base_liquidity_state} ➔ {result.scenario_liquidity_state}</span>
                )}
              </div>

              {/* 1. Primary Spendable Capacity Comparison */}
              <div className="before-after-grid">
                <div className="comparison-box before-box">
                  <span className="box-title">BEFORE (SPENDABLE)</span>
                  <span className="box-amount">
                    {formatCurrency(result.base_spendable_amount ?? result.base_spendable ?? 0)}
                  </span>
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
                  <span className="box-amount scenario-highlight">
                    {formatCurrency(result.scenario_spendable_amount ?? result.scenario_spendable ?? 0)}
                  </span>
                  {scenarioBadge && (
                    <span className="mini-status-badge" style={{ color: scenarioBadge.color }}>
                      {scenarioBadge.label}
                    </span>
                  )}
                </div>
              </div>

              {/* 2. Detailed Multi-Metric Financial Breakdown Grid */}
              <div className="scenario-metrics-grid">
                <div className="metric-impact-card">
                  <span className="metric-impact-label">Account Balance</span>
                  <div className="metric-impact-vals">
                    <span className="prev-val">{formatCurrency(result.base_current_balance ?? 0)}</span>
                    <span className="arr">➔</span>
                    <span className="curr-val">{formatCurrency(result.scenario_current_balance ?? 0)}</span>
                  </div>
                </div>

                <div className="metric-impact-card">
                  <span className="metric-impact-label">30-Day Minimum Runway</span>
                  <div className="metric-impact-vals">
                    <span className="prev-val">{formatCurrency(result.base_forecasted_minimum_balance ?? 0)}</span>
                    <span className="arr">➔</span>
                    <span className="curr-val" style={{ color: (result.scenario_forecasted_minimum_balance ?? 0) < 0 ? '#ef4444' : '#00e5a3' }}>
                      {formatCurrency(result.scenario_forecasted_minimum_balance ?? 0)}
                    </span>
                  </div>
                </div>

                <div className="metric-impact-card">
                  <span className="metric-impact-label">Protected Safety Buffer</span>
                  <div className="metric-impact-vals">
                    <span className="prev-val">{formatCurrency(result.base_safety_reserve ?? 0)}</span>
                    <span className="arr">➔</span>
                    <span className="curr-val">{formatCurrency(result.scenario_safety_reserve ?? 0)}</span>
                  </div>
                </div>
              </div>

              {/* 3. Scenario Insights & Actionable Guidance */}
              <div className="scenario-explanation-box">
                <div className="explanation-header">
                  <Shield size={16} color="#00e5a3" />
                  <h4>Financial Impact Analysis</h4>
                </div>
                <p>
                  {result.explanation ||
                    `Simulating this scenario changes your immediate spendable capacity by ${formatCurrency(result.spendable_delta)}. Your 30-day minimum projected balance shifts from ${formatCurrency(result.base_forecasted_minimum_balance ?? 0)} to ${formatCurrency(result.scenario_forecasted_minimum_balance ?? 0)}.`}
                </p>
                <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <button
                    type="button"
                    className="secondary-btn compact"
                    onClick={() => {
                      setIsAiOpen(true);
                      handleSendChatMessage(`How does this simulated scenario (${result.scenario_description || 'scenario'}) affect my 30-day liquidity and recurring bill payments?`);
                    }}
                  >
                    <Bot size={14} color="#00e5a3" />
                    <span>Ask Spendable AI about this scenario</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ==========================================================================
         SPENDABLE AI ASSISTANT SECTION (COLLAPSIBLE CTA + FULL CHAT)
         ========================================================================== */}
      {!isAiOpen ? (
        <div className="spendable-ai-cta-banner" onClick={() => setIsAiOpen(true)}>
          <div className="cta-banner-left">
            <div className="cta-banner-icon">
              <Bot size={26} />
            </div>
            <div className="cta-banner-text">
              <h3>
                Spendable AI Financial Assistant
                <Sparkles size={16} color="#00e5a3" />
              </h3>
              <p>Ask anything about your safe spending runway, 30-day cash-flow forecast, or scenario simulations.</p>
            </div>
          </div>
          <button className="cta-banner-btn" type="button" onClick={(e) => { e.stopPropagation(); setIsAiOpen(true); }}>
            <MessageSquare size={16} />
            <span>Launch Spendable AI</span>
            <ChevronDown size={16} />
          </button>
        </div>
      ) : (
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

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
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
              <button
                type="button"
                className="chat-collapse-btn"
                onClick={() => setIsAiOpen(false)}
                title="Collapse Spendable AI Chat"
              >
                <ChevronUp size={14} />
                <span>Collapse AI</span>
              </button>
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
                  {msg.role === 'assistant' ? renderFormattedContent(msg.content) : <div>{msg.content}</div>}
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
      )}
    </div>
  );
};
