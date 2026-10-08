import React from 'react';

const AuthInput = ({ label, id, error, ...props }) => {
  return (
    <div className="input-group">
      <label htmlFor={id} className="input-label">{label}</label>
      <div className="input-wrapper">
        <input 
          id={id}
          className={`input-field ${error ? 'error' : ''}`}
          {...props}
        />
      </div>
      {error && <span className="input-error-msg">{error}</span>}
    </div>
  );
};

export default AuthInput;
