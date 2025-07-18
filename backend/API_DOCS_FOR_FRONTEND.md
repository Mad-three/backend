# 🚀 PresentationAngel Backend API 가이드 (프론트엔드용)

안녕하세요! 백엔드 API 연동을 위한 가이드입니다.  
React + WebSocket을 사용해서 실시간 텍스트 에코 기능을 구현할 수 있습니다.

---

## 📋 목차
- [서버 정보](#-서버-정보)
- [WebSocket 연결](#-websocket-연결)
- [메시지 형식](#-메시지-형식)
- [React 구현 예시](#-react-구현-예시)
- [에러 처리](#-에러-처리)
- [테스트 방법](#-테스트-방법)
- [문제해결](#-문제해결)

---

## 🌐 서버 정보

### 기본 설정
- **서버 주소**: `localhost` (개발환경)
- **포트**: `8000`
- **WebSocket 엔드포인트**: `ws://localhost:8000/ws`

### REST API 엔드포인트
- `GET http://localhost:8000/` - 서버 상태 확인
- `GET http://localhost:8000/health` - 헬스 체크

### CORS 설정
다음 주소들이 허용되어 있습니다:
- `http://localhost:3000` (Create React App)
- `http://localhost:5173` (Vite)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

---

## 🔌 WebSocket 연결

### 기본 연결
```javascript
const websocket = new WebSocket('ws://localhost:8000/ws');

// 연결 성공
websocket.onopen = (event) => {
    console.log('WebSocket 연결 성공!');
};

// 연결 해제
websocket.onclose = (event) => {
    console.log('WebSocket 연결 해제됨');
};

// 에러 처리
websocket.onerror = (error) => {
    console.error('WebSocket 에러:', error);
};
```

### 연결 시 자동 메시지
WebSocket 연결이 성공하면 서버에서 자동으로 환영 메시지를 보냅니다:
```json
{
    "type": "connection",
    "message": "WebSocket 연결이 성공했습니다",
    "timestamp": "2024-01-01T12:00:00.000000",
    "connections": 1
}
```

---

## 📨 메시지 형식

### 프론트엔드 → 백엔드 (메시지 전송)
```json
{
    "message": "Hello, World"
}
```

**JavaScript 전송 예시:**
```javascript
const messageData = {
    message: "Hello, World"
};
websocket.send(JSON.stringify(messageData));
```

### 백엔드 → 프론트엔드 (에코 응답)
```json
{
    "echo": "Hello, World",
    "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 에러 응답
```json
{
    "error": "메시지 처리 중 오류: [에러내용]",
    "timestamp": "2024-01-01T12:00:00.000000"
}
```

---

## ⚛️ React 구현 예시

### 1. 기본 Hook 구현
```javascript
import { useState, useEffect, useRef } from 'react';

const useWebSocket = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState([]);
    const [error, setError] = useState(null);
    const websocketRef = useRef(null);

    // WebSocket 연결
    const connect = () => {
        try {
            const ws = new WebSocket('ws://localhost:8000/ws');
            
            ws.onopen = () => {
                setIsConnected(true);
                setError(null);
                console.log('WebSocket 연결됨');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setMessages(prev => [...prev, {
                        type: 'received',
                        data: data,
                        timestamp: new Date()
                    }]);
                } catch (err) {
                    console.error('메시지 파싱 오류:', err);
                }
            };

            ws.onclose = () => {
                setIsConnected(false);
                console.log('WebSocket 연결 해제됨');
            };

            ws.onerror = (error) => {
                setError('WebSocket 연결 오류');
                console.error('WebSocket 에러:', error);
            };

            websocketRef.current = ws;
        } catch (err) {
            setError('WebSocket 연결 실패');
        }
    };

    // 메시지 전송
    const sendMessage = (message) => {
        if (websocketRef.current && isConnected) {
            const messageData = { message };
            websocketRef.current.send(JSON.stringify(messageData));
            
            // 전송된 메시지를 로그에 추가
            setMessages(prev => [...prev, {
                type: 'sent',
                data: { message },
                timestamp: new Date()
            }]);
        } else {
            setError('WebSocket이 연결되지 않았습니다');
        }
    };

    // 연결 해제
    const disconnect = () => {
        if (websocketRef.current) {
            websocketRef.current.close();
        }
    };

    // 컴포넌트 언마운트 시 연결 정리
    useEffect(() => {
        return () => {
            if (websocketRef.current) {
                websocketRef.current.close();
            }
        };
    }, []);

    return {
        isConnected,
        messages,
        error,
        connect,
        disconnect,
        sendMessage
    };
};

export default useWebSocket;
```

### 2. 컴포넌트 사용 예시
```javascript
import React, { useState } from 'react';
import useWebSocket from './hooks/useWebSocket';

const ChatComponent = () => {
    const [inputMessage, setInputMessage] = useState('Hello, World');
    const { isConnected, messages, error, connect, disconnect, sendMessage } = useWebSocket();

    const handleSendMessage = () => {
        if (inputMessage.trim()) {
            sendMessage(inputMessage.trim());
            setInputMessage('');
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '600px' }}>
            <h2>WebSocket 테스트</h2>
            
            {/* 연결 상태 */}
            <div style={{ 
                padding: '10px', 
                backgroundColor: isConnected ? '#d4edda' : '#f8d7da',
                color: isConnected ? '#155724' : '#721c24',
                marginBottom: '10px'
            }}>
                상태: {isConnected ? '연결됨' : '연결 안됨'}
            </div>

            {/* 에러 메시지 */}
            {error && (
                <div style={{ color: 'red', marginBottom: '10px' }}>
                    에러: {error}
                </div>
            )}

            {/* 연결/해제 버튼 */}
            <div style={{ marginBottom: '20px' }}>
                <button 
                    onClick={connect} 
                    disabled={isConnected}
                    style={{ marginRight: '10px' }}
                >
                    연결
                </button>
                <button 
                    onClick={disconnect} 
                    disabled={!isConnected}
                >
                    해제
                </button>
            </div>

            {/* 메시지 입력 */}
            <div style={{ marginBottom: '20px' }}>
                <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={!isConnected}
                    placeholder="메시지를 입력하세요..."
                    style={{ 
                        padding: '8px', 
                        width: '300px', 
                        marginRight: '10px' 
                    }}
                />
                <button 
                    onClick={handleSendMessage}
                    disabled={!isConnected || !inputMessage.trim()}
                >
                    전송
                </button>
            </div>

            {/* 메시지 로그 */}
            <div style={{ 
                border: '1px solid #ccc', 
                height: '300px', 
                overflowY: 'auto',
                padding: '10px',
                backgroundColor: '#f9f9f9'
            }}>
                {messages.map((msg, index) => (
                    <div key={index} style={{ marginBottom: '5px' }}>
                        <span style={{ color: '#666', fontSize: '12px' }}>
                            [{msg.timestamp.toLocaleTimeString()}]
                        </span>
                        <span style={{ 
                            color: msg.type === 'sent' ? 'blue' : 'green',
                            marginLeft: '5px'
                        }}>
                            {msg.type === 'sent' ? '📤 전송' : '📥 수신'}:
                        </span>
                        <span style={{ marginLeft: '5px' }}>
                            {msg.type === 'sent' 
                                ? msg.data.message 
                                : (msg.data.echo || JSON.stringify(msg.data))
                            }
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ChatComponent;
```

---

## ❌ 에러 처리

### 일반적인 에러 상황들

1. **서버 연결 실패**
   ```javascript
   websocket.onerror = (error) => {
       console.error('서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.');
   };
   ```

2. **JSON 파싱 에러**
   ```javascript
   websocket.onmessage = (event) => {
       try {
           const data = JSON.parse(event.data);
           // 정상 처리
       } catch (error) {
           console.error('올바르지 않은 JSON 형식:', event.data);
       }
   };
   ```

3. **메시지 전송 실패**
   ```javascript
   const sendMessage = (message) => {
       if (websocket.readyState === WebSocket.OPEN) {
           websocket.send(JSON.stringify({ message }));
       } else {
           console.error('WebSocket이 연결되지 않았습니다.');
       }
   };
   ```

---

## 🧪 테스트 방법

### 1. 백엔드 서버 실행 확인
브라우저에서 `http://localhost:8000` 접속해서 서버 상태 확인

### 2. WebSocket 연결 테스트
```javascript
// 브라우저 개발자 도구 콘솔에서
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (e) => console.log('받은 메시지:', JSON.parse(e.data));
ws.send(JSON.stringify({ message: "테스트" }));
```

### 3. 백엔드 제공 테스트 페이지
`backend/test.html` 파일을 브라우저로 열어서 기능 테스트 가능

---

## 🔧 문제해결

### 자주 발생하는 문제들

**Q: WebSocket 연결이 안 돼요!**
- 백엔드 서버가 실행 중인지 확인 (`python main.py`)
- 포트 8000이 사용 중인지 확인
- 브라우저 콘솔에서 에러 메시지 확인

**Q: CORS 에러가 발생해요!**
- 프론트엔드 주소가 백엔드의 CORS 설정에 포함되어 있는지 확인
- `backend/config.py`의 `ALLOWED_ORIGINS`에 주소 추가

**Q: 메시지가 전송은 되는데 응답이 안 와요!**
- 메시지 형식이 올바른지 확인: `{ "message": "내용" }`
- 백엔드 콘솔에서 에러 로그 확인

**Q: Docker 환경에서 연결이 안 돼요!**
- WebSocket 주소를 `ws://localhost:8000/ws`에서 적절한 Docker 컨테이너 주소로 변경
- 네트워크 설정 및 포트 매핑 확인

---

## 📞 연락처

백엔드 관련 문의사항이나 API 수정 요청은 백엔드 팀에게 연락주세요!

### 현재 구현된 기능
✅ WebSocket 실시간 연결  
✅ 텍스트 메시지 에코  
✅ 연결 상태 관리  
✅ 에러 처리  

### 향후 추가 예정 기능
🔄 음성-텍스트 변환  
🔄 대본 비교 기능  
🔄 실시간 피드백  

---

**Happy Coding! 🚀** 