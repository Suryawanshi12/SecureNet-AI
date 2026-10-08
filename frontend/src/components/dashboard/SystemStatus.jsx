import React, { useEffect, useState } from 'react';
import { getHealth, getModelInfo } from '../../api/authApi';

const SystemStatus = () => {
  const [statusState, setStatusState] = useState({
    apiStatus: 'Checking...',
    xgboostModel: 'Checking...',
    isolationForest: 'Checking...',
    shapEngine: 'Checking...',
    riskEngine: 'Checking...',
    isLoading: true,
    isError: false,
  });

  useEffect(() => {
    let isMounted = true;

    const fetchSystemStatus = async () => {
      try {
        const [healthRes, modelRes] = await Promise.allSettled([
          getHealth(),
          getModelInfo(),
        ]);

        if (!isMounted) return;

        const apiOnline = healthRes.status === 'fulfilled' && healthRes.value?.data?.status === 'healthy';
        const modelData = modelRes.status === 'fulfilled' ? modelRes.value?.data : null;

        setStatusState({
          apiStatus: apiOnline ? 'Online' : 'Offline',
          xgboostModel: modelData?.supervised_model ? `${modelData.supervised_model}` : (apiOnline ? 'Online' : 'Unknown'),
          isolationForest: modelData?.anomaly_model ? `${modelData.anomaly_model}` : (apiOnline ? 'Online' : 'Unknown'),
          shapEngine: modelData?.explainability ? `${modelData.explainability}` : (apiOnline ? 'Online' : 'Unknown'),
          riskEngine: modelData?.risk_scoring ? `${modelData.risk_scoring}` : (apiOnline ? 'Online' : 'Unknown'),
          isLoading: false,
          isError: !apiOnline,
        });
      } catch (err) {
        if (!isMounted) return;
        setStatusState({
          apiStatus: 'Offline',
          xgboostModel: 'Unknown',
          isolationForest: 'Unknown',
          shapEngine: 'Unknown',
          riskEngine: 'Unknown',
          isLoading: false,
          isError: true,
        });
      }
    };

    fetchSystemStatus();

    return () => {
      isMounted = false;
    };
  }, []);

  const getStatusBadge = (statusText) => {
    if (statusText === 'Checking...') {
      return <span className="status-pill status-loading">Checking...</span>;
    }
    if (statusText === 'Offline' || statusText === 'Unknown') {
      return (
        <span className="status-pill status-offline">
          <span className="status-dot offline-dot" />
          {statusText}
        </span>
      );
    }
    return (
      <span className="status-pill status-online">
        <span className="status-dot online-dot" />
        {statusText}
      </span>
    );
  };

  return (
    <div className="soc-panel system-status-panel">
      <div className="panel-header">
        <h2 className="panel-title">System Status</h2>
        <span className="panel-badge">Live Verification</span>
      </div>

      <div className="panel-body">
        {statusState.isLoading ? (
          <div className="status-loading-box">
            <div className="spinner-small" />
            <span>Loading security data...</span>
          </div>
        ) : (
          <div className="system-status-list">
            <div className="status-item">
              <span className="status-name">API Endpoint</span>
              {getStatusBadge(statusState.apiStatus)}
            </div>

            <div className="status-item">
              <span className="status-name">XGBoost Model</span>
              {getStatusBadge(statusState.xgboostModel)}
            </div>

            <div className="status-item">
              <span className="status-name">Isolation Forest</span>
              {getStatusBadge(statusState.isolationForest)}
            </div>

            <div className="status-item">
              <span className="status-name">SHAP Explainability</span>
              {getStatusBadge(statusState.shapEngine)}
            </div>

            <div className="status-item">
              <span className="status-name">Risk Engine</span>
              {getStatusBadge(statusState.riskEngine)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemStatus;
