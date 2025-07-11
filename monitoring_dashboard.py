#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실시간 모니터링 대시보드
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import logging

logger = logging.getLogger(__name__)

class MonitoringDashboard:
    """실시간 모니터링 대시보드"""
    
    def __init__(self):
        self.app = FastAPI(title="뉴스 분석 모니터링 대시보드")
        self.active_connections: List[WebSocket] = []
        self.metrics_history: List[Dict] = []
        self.setup_routes()
    
    def setup_routes(self):
        """라우트 설정"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def get_dashboard():
            return self.get_dashboard_html()
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            try:
                while True:
                    # 실시간 메트릭 전송
                    metrics = await self.get_realtime_metrics()
                    await websocket.send_text(json.dumps(metrics))
                    await asyncio.sleep(5)  # 5초마다 업데이트
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    def get_dashboard_html(self) -> str:
        """대시보드 HTML 반환"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>뉴스 분석 모니터링 대시보드</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .metric { text-align: center; margin: 10px 0; }
                .metric-value { font-size: 2em; font-weight: bold; color: #2196F3; }
                .metric-label { color: #666; margin-top: 5px; }
                .status-good { color: #4CAF50; }
                .status-warning { color: #FF9800; }
                .status-error { color: #F44336; }
                .chart-container { height: 300px; }
            </style>
        </head>
        <body>
            <h1>📊 뉴스 분석 모니터링 대시보드</h1>
            <div class="dashboard">
                <div class="card">
                    <h3>실시간 성능 지표</h3>
                    <div class="metric">
                        <div class="metric-value" id="success-rate">-</div>
                        <div class="metric-label">성공률</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="avg-processing-time">-</div>
                        <div class="metric-label">평균 처리시간 (초)</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="total-processed">-</div>
                        <div class="metric-label">총 처리된 뉴스</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>분석 품질 지표</h3>
                    <div class="metric">
                        <div class="metric-value" id="sentiment-confidence">-</div>
                        <div class="metric-label">감정분석 신뢰도</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="stock-confidence">-</div>
                        <div class="metric-label">종목추출 신뢰도</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="keyword-diversity">-</div>
                        <div class="metric-label">키워드 다양성</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>시스템 상태</h3>
                    <div class="metric">
                        <div class="metric-value" id="system-status">정상</div>
                        <div class="metric-label">시스템 상태</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="last-update">-</div>
                        <div class="metric-label">마지막 업데이트</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="active-connections">-</div>
                        <div class="metric-label">활성 연결</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>감정 분포</h3>
                    <div class="chart-container">
                        <canvas id="sentimentChart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <h3>처리량 트렌드</h3>
                    <div class="chart-container">
                        <canvas id="processingChart"></canvas>
                    </div>
                </div>
            </div>
            
            <script>
                const ws = new WebSocket('ws://localhost:8001/ws');
                const sentimentChart = new Chart(document.getElementById('sentimentChart'), {
                    type: 'doughnut',
                    data: {
                        labels: ['긍정', '부정', '중립'],
                        datasets: [{
                            data: [30, 20, 50],
                            backgroundColor: ['#4CAF50', '#F44336', '#FF9800']
                        }]
                    }
                });
                
                const processingChart = new Chart(document.getElementById('processingChart'), {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: '처리량',
                            data: [],
                            borderColor: '#2196F3',
                            tension: 0.1
                        }]
                    },
                    options: {
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    // 메트릭 업데이트
                    document.getElementById('success-rate').textContent = (data.success_rate * 100).toFixed(1) + '%';
                    document.getElementById('avg-processing-time').textContent = data.avg_processing_time.toFixed(2);
                    document.getElementById('total-processed').textContent = data.total_processed;
                    document.getElementById('sentiment-confidence').textContent = (data.sentiment_confidence * 100).toFixed(1) + '%';
                    document.getElementById('stock-confidence').textContent = (data.stock_confidence * 100).toFixed(1) + '%';
                    document.getElementById('keyword-diversity').textContent = data.keyword_diversity;
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                    document.getElementById('active-connections').textContent = data.active_connections;
                    
                    // 차트 업데이트
                    if (data.sentiment_distribution) {
                        sentimentChart.data.datasets[0].data = [
                            data.sentiment_distribution.positive || 0,
                            data.sentiment_distribution.negative || 0,
                            data.sentiment_distribution.neutral || 0
                        ];
                        sentimentChart.update();
                    }
                    
                    // 처리량 차트 업데이트
                    const now = new Date().toLocaleTimeString();
                    processingChart.data.labels.push(now);
                    processingChart.data.datasets[0].data.push(data.total_processed);
                    
                    if (processingChart.data.labels.length > 20) {
                        processingChart.data.labels.shift();
                        processingChart.data.datasets[0].data.shift();
                    }
                    processingChart.update();
                };
                
                ws.onclose = function() {
                    document.getElementById('system-status').textContent = '연결 끊김';
                    document.getElementById('system-status').className = 'metric-value status-error';
                };
            </script>
        </body>
        </html>
        """
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """실시간 메트릭 수집"""
        try:
            # 실제로는 MongoDB에서 데이터를 가져와야 함
            # 여기서는 샘플 데이터를 반환
            return {
                "success_rate": 0.95,
                "avg_processing_time": 3.2,
                "total_processed": 1250,
                "sentiment_confidence": 0.75,
                "stock_confidence": 0.82,
                "keyword_diversity": 5.3,
                "active_connections": len(self.active_connections),
                "sentiment_distribution": {
                    "positive": 35,
                    "negative": 25,
                    "neutral": 40
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"메트릭 수집 실패: {e}")
            return {
                "success_rate": 0.0,
                "avg_processing_time": 0.0,
                "total_processed": 0,
                "sentiment_confidence": 0.0,
                "stock_confidence": 0.0,
                "keyword_diversity": 0,
                "active_connections": 0,
                "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                "timestamp": datetime.now().isoformat()
            }
    
    def broadcast_metrics(self, metrics: Dict[str, Any]):
        """모든 연결된 클라이언트에 메트릭 브로드캐스트"""
        for connection in self.active_connections:
            try:
                asyncio.create_task(connection.send_text(json.dumps(metrics)))
            except Exception as e:
                logger.error(f"메트릭 브로드캐스트 실패: {e}")
                self.active_connections.remove(connection)

# 전역 대시보드 인스턴스
dashboard = MonitoringDashboard()

def run_dashboard():
    """대시보드 실행"""
    import uvicorn
    uvicorn.run(dashboard.app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    run_dashboard() 