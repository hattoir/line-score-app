import React from 'react';
import { Link } from 'react-router-dom';

const DiagnosisPage = () => {
  return (
    <div className="diagnosis-page">
      <h1>性格診断ページ</h1>
      <p>ここで性格診断の機能を作成していきます。</p>
      <br />
      <Link to="/" className="diagnosis-button">戻る</Link>
    </div>
  );
};

export default DiagnosisPage;