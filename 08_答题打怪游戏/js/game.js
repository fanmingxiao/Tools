/**
 * 勇者斗恶龙 - 答题打怪游戏
 * 主游戏逻辑文件
 */

// ===== 游戏状态管理 =====
const GameState = {
    questions: [],        // 题库
    currentQuestions: [], // 当前轮次的20道题
    currentIndex: 0,      // 当前题目索引
    correctCount: 0,      // 本轮正确数量
    totalCorrect: 0,      // 总计答对数量（跨关卡累计）
    level: 1,             // 当前关卡
    timer: null,          // 计时器
    timeLeft: 30,         // 剩余时间
    isAnswering: false,   // 是否正在答题
    wrongQuestions: [],   // 本轮错题记录
};

// 错题本存储键名
const WRONG_BOOK_KEY = 'dragonQuest_wrongBook';

// 怪物配置
const MONSTERS = [
    { name: '史莱姆', color: '#8b5cf6', eyeColor: '#ef4444', scale: 1 },
    { name: '哥布林', color: '#22c55e', eyeColor: '#fbbf24', scale: 1.15 },
    { name: '骷髅兵', color: '#94a3b8', eyeColor: '#ef4444', scale: 1.3 },
    { name: '狼人', color: '#78716c', eyeColor: '#fcd34d', scale: 1.45 },
    { name: '石像鬼', color: '#6b7280', eyeColor: '#f97316', scale: 1.6 },
    { name: '火焰魔', color: '#ef4444', eyeColor: '#fbbf24', scale: 1.75 },
    { name: '冰霜巨人', color: '#38bdf8', eyeColor: '#ffffff', scale: 1.9 },
    { name: '暗影龙', color: '#1e1b4b', eyeColor: '#a855f7', scale: 2.1 },
    { name: '混沌领主', color: '#be123c', eyeColor: '#000000', scale: 2.3 },
    { name: '毁灭之王', color: '#000000', eyeColor: '#ef4444', scale: 2.5 },
];

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
});

function initEventListeners() {
    // CSV文件上传
    document.getElementById('csv-file').addEventListener('change', handleCSVUpload);

    // 开始游戏按钮
    document.getElementById('start-btn').addEventListener('click', startGame);

    // 选项按钮
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.addEventListener('click', () => handleAnswer(btn.dataset.option));
    });
}

// ===== CSV解析 =====
function handleCSVUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const content = e.target.result;
            parseCSV(content);
        } catch (error) {
            showUploadStatus('解析失败：' + error.message, false);
        }
    };
    reader.readAsText(file, 'UTF-8');
}

function parseCSV(content) {
    const lines = content.split('\n').filter(line => line.trim());
    const questions = [];

    // 跳过标题行（如果有）
    let startIndex = 0;
    const firstLine = lines[0].toLowerCase();
    if (firstLine.includes('题目') || firstLine.includes('question')) {
        startIndex = 1;
    }

    for (let i = startIndex; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        // 解析CSV行，处理可能的引号
        const parts = parseCSVLine(line);

        if (parts.length >= 6) {
            questions.push({
                question: parts[0],
                optionA: parts[1],
                optionB: parts[2],
                optionC: parts[3],
                optionD: parts[4],
                answer: parts[5].toUpperCase().trim()
            });
        }
    }

    if (questions.length < 20) {
        showUploadStatus(`题库至少需要20道题目，当前只有${questions.length}道`, false);
        return;
    }

    GameState.questions = questions;
    showUploadStatus(`✅ 题库导入成功，共${questions.length}道题目`, true);
    document.getElementById('start-btn').disabled = false;
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }

    result.push(current.trim());
    return result;
}

function showUploadStatus(message, success) {
    const statusEl = document.getElementById('upload-status');
    statusEl.textContent = message;
    statusEl.className = 'upload-status' + (success ? ' success' : '');
}

// ===== 游戏控制 =====
function startGame() {
    // 重置游戏状态
    GameState.currentIndex = 0;
    GameState.correctCount = 0;
    GameState.wrongQuestions = [];  // 重置本轮错题

    // 随机选择20道题
    GameState.currentQuestions = shuffleArray([...GameState.questions]).slice(0, 20);

    // 切换到游戏界面
    showScreen('game-screen');

    // 更新怪物
    updateMonster();

    // 更新UI
    updateGameUI();

    // 显示第一道题
    showQuestion();
}

function showQuestion() {
    const question = GameState.currentQuestions[GameState.currentIndex];

    // 更新题目显示
    document.getElementById('question-text').textContent = question.question;
    document.getElementById('option-a').textContent = question.optionA;
    document.getElementById('option-b').textContent = question.optionB;
    document.getElementById('option-c').textContent = question.optionC;
    document.getElementById('option-d').textContent = question.optionD;

    // 重置选项状态
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.classList.remove('correct', 'wrong');
        btn.disabled = false;
    });

    // 开始计时
    GameState.timeLeft = 30;
    GameState.isAnswering = true;
    startTimer();
}

function startTimer() {
    updateTimerDisplay();

    GameState.timer = setInterval(() => {
        GameState.timeLeft--;
        updateTimerDisplay();

        if (GameState.timeLeft <= 0) {
            clearInterval(GameState.timer);
            handleTimeout();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const timerBar = document.getElementById('timer-bar');
    const timerText = document.getElementById('timer-text');

    const percentage = (GameState.timeLeft / 30) * 100;
    timerBar.style.width = percentage + '%';
    timerText.textContent = GameState.timeLeft;

    // 更新颜色
    timerBar.classList.remove('warning', 'danger');
    if (GameState.timeLeft <= 10) {
        timerBar.classList.add('danger');
    } else if (GameState.timeLeft <= 20) {
        timerBar.classList.add('warning');
    }
}

function handleTimeout() {
    if (!GameState.isAnswering) return;

    GameState.isAnswering = false;

    // 超时也记录为错题
    const question = GameState.currentQuestions[GameState.currentIndex];
    recordWrongQuestion(question, '超时未答');

    // 显示正确答案
    const correctAnswer = question.answer;
    highlightAnswer(null, correctAnswer);

    // 画面震动
    shakeBattleArea();

    // 延迟后进入下一题
    setTimeout(() => {
        nextQuestion();
    }, 1500);
}

function handleAnswer(selectedOption) {
    if (!GameState.isAnswering) return;

    GameState.isAnswering = false;
    clearInterval(GameState.timer);

    const question = GameState.currentQuestions[GameState.currentIndex];
    const isCorrect = selectedOption === question.answer;

    // 禁用所有选项
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.disabled = true;
    });

    // 高亮答案
    highlightAnswer(selectedOption, question.answer);

    if (isCorrect) {
        GameState.correctCount++;
        // 怪物受击效果
        hitMonster();
        // 更新怪物血条
        updateMonsterHP();
    } else {
        // 记录错题
        recordWrongQuestion(question, selectedOption);
        // 画面震动
        shakeBattleArea();
    }

    // 更新UI
    updateGameUI();

    // 延迟后进入下一题
    setTimeout(() => {
        nextQuestion();
    }, 1500);
}

function highlightAnswer(selected, correct) {
    document.querySelectorAll('.option-btn').forEach(btn => {
        if (btn.dataset.option === correct) {
            btn.classList.add('correct');
        } else if (btn.dataset.option === selected && selected !== correct) {
            btn.classList.add('wrong');
        }
    });
}

function nextQuestion() {
    GameState.currentIndex++;

    if (GameState.currentIndex >= 20) {
        endGame();
    } else {
        updateGameUI();
        showQuestion();
    }
}

function updateGameUI() {
    document.getElementById('level-num').textContent = GameState.level;
    document.getElementById('current-q').textContent = GameState.currentIndex + 1;
    document.getElementById('correct-count').textContent = GameState.correctCount;
}

// ===== 怪物效果 =====
function updateMonster() {
    const monsterIndex = Math.min(GameState.level - 1, MONSTERS.length - 1);
    const monster = MONSTERS[monsterIndex];

    const monsterEl = document.getElementById('monster');
    const monsterName = document.getElementById('monster-name');
    const container = document.getElementById('monster-container');

    // 更新怪物样式
    document.documentElement.style.setProperty('--monster-color', monster.color);
    document.documentElement.style.setProperty('--monster-eye', monster.eyeColor);
    container.style.transform = `scale(${monster.scale})`;
    monsterName.textContent = monster.name;

    // 重置怪物状态
    monsterEl.classList.remove('hit', 'dying');

    // 重置血条
    document.getElementById('monster-hp').style.width = '100%';
}

function updateMonsterHP() {
    // 血量根据正确率变化
    const totalAnswered = GameState.currentIndex + 1;
    const damagePerCorrect = 100 / 12; // 答对12题就能打满
    const remainingHP = Math.max(0, 100 - (GameState.correctCount * damagePerCorrect));

    document.getElementById('monster-hp').style.width = remainingHP + '%';
}

function hitMonster() {
    const monsterEl = document.getElementById('monster');
    monsterEl.classList.add('hit');
    setTimeout(() => {
        monsterEl.classList.remove('hit');
    }, 300);
}

function shakeBattleArea() {
    const battleArea = document.getElementById('battle-area');
    battleArea.classList.add('shake');
    setTimeout(() => {
        battleArea.classList.remove('shake');
    }, 500);
}

// ===== 游戏结束 =====
function endGame() {
    clearInterval(GameState.timer);

    // 保存本轮错题到错题本
    saveWrongQuestionsToBook();

    const accuracy = (GameState.correctCount / 20) * 100;
    const isVictory = accuracy >= 60;

    if (isVictory) {
        // 胜利动画
        showVictoryAnimation();
    } else {
        // 直接显示失败结果
        showResult(false);
    }
}

function showVictoryAnimation() {
    const battleArea = document.getElementById('battle-area');
    const monsterEl = document.getElementById('monster');

    // 画面闪动
    battleArea.classList.add('victory-flash');

    // 怪物渐渐消失
    monsterEl.classList.add('dying');

    setTimeout(() => {
        battleArea.classList.remove('victory-flash');
        showResult(true);
    }, 2000);
}

function showResult(isVictory) {
    const container = document.getElementById('result-container');
    const accuracy = (GameState.correctCount / 20) * 100;
    const wrongBook = loadWrongBook();
    const wrongCount = GameState.wrongQuestions.length;
    const totalWrongCount = wrongBook.length;

    // 累加本轮正确数到总计
    GameState.totalCorrect += GameState.correctCount;

    // 统计信息
    const statsHTML = `
        <div class="stat-item">
            <span class="stat-label">关卡</span>
            <span class="stat-value">${GameState.level}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">本轮答对</span>
            <span class="stat-value">${GameState.correctCount} / 20</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">正确率</span>
            <span class="stat-value">${accuracy.toFixed(1)}%</span>
        </div>
        <div class="stat-item highlight">
            <span class="stat-label">🌟 总计答对</span>
            <span class="stat-value">${GameState.totalCorrect} 道</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">本轮错题</span>
            <span class="stat-value">${wrongCount} 道</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">错题本总计</span>
            <span class="stat-value">${totalWrongCount} 道</span>
        </div>
    `;

    if (isVictory) {
        container.innerHTML = `
            <div class="result-icon">🏆</div>
            <h1 class="result-title victory">恭喜胜利!</h1>
            <div class="result-stats">
                ${statsHTML}
            </div>
            <p class="result-message">是否挑战下一个？</p>
            <div class="result-buttons">
                <button class="result-btn primary" onclick="continueGame()">⚔️ 继续挑战</button>
                <button class="result-btn secondary" onclick="exitGame()">🚪 退出游戏</button>
            </div>
            <div class="result-buttons" style="margin-top: 10px;">
                <button class="result-btn tertiary" onclick="downloadWrongBook()">📥 下载错题本 (${totalWrongCount}道)</button>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="result-icon">💀</div>
            <h1 class="result-title defeat">大侠请重新来过</h1>
            <div class="result-stats">
                ${statsHTML}
            </div>
            <p class="result-message">需要60%以上的正确率才能击败怪物</p>
            <div class="result-buttons">
                <button class="result-btn primary" onclick="restartGame()">🔄 重新挑战</button>
                <button class="result-btn secondary" onclick="exitGame()">🚪 退出游戏</button>
            </div>
            <div class="result-buttons" style="margin-top: 10px;">
                <button class="result-btn tertiary" onclick="downloadWrongBook()">📥 下载错题本 (${totalWrongCount}道)</button>
            </div>
        `;
    }

    showScreen('result-screen');
}

function continueGame() {
    GameState.level++;
    startGame();
}

function restartGame() {
    GameState.level = 1;
    startGame();
}

function exitGame() {
    GameState.level = 1;
    GameState.totalCorrect = 0;  // 重置总计答对数
    showScreen('start-screen');
}

// ===== 工具函数 =====
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

// ===== 错题本功能 =====

// 记录错题到本轮错题列表
function recordWrongQuestion(question, playerAnswer) {
    GameState.wrongQuestions.push({
        question: question.question,
        optionA: question.optionA,
        optionB: question.optionB,
        optionC: question.optionC,
        optionD: question.optionD,
        correctAnswer: question.answer,
        playerAnswer: playerAnswer,
        timestamp: new Date().toISOString()
    });
}

// 从localStorage加载错题本
function loadWrongBook() {
    try {
        const data = localStorage.getItem(WRONG_BOOK_KEY);
        return data ? JSON.parse(data) : [];
    } catch (e) {
        console.error('加载错题本失败:', e);
        return [];
    }
}

// 保存本轮错题到错题本（去重合并）
function saveWrongQuestionsToBook() {
    if (GameState.wrongQuestions.length === 0) return;

    const wrongBook = loadWrongBook();

    // 合并新错题，根据题目内容去重
    GameState.wrongQuestions.forEach(newWrong => {
        const exists = wrongBook.some(existing =>
            existing.question === newWrong.question
        );
        if (!exists) {
            wrongBook.push(newWrong);
        }
    });

    try {
        localStorage.setItem(WRONG_BOOK_KEY, JSON.stringify(wrongBook));
        console.log(`错题本已更新，共${wrongBook.length}道题`);
    } catch (e) {
        console.error('保存错题本失败:', e);
    }
}

// 下载错题本为CSV文件
function downloadWrongBook() {
    const wrongBook = loadWrongBook();
    if (wrongBook.length === 0) {
        alert('错题本为空！');
        return;
    }

    // 转义CSV字段中的特殊字符
    function escapeCSV(str) {
        if (str === undefined || str === null) return '';
        str = String(str);
        // 如果包含逗号、引号或换行符，需要用引号包裹
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            // 转义内部的引号
            str = str.replace(/"/g, '""');
            return `"${str}"`;
        }
        return str;
    }

    // 构建CSV内容
    let csvContent = '题目,A选项,B选项,C选项,D选项,正确答案,你的答案,记录时间\n';

    wrongBook.forEach(item => {
        const row = [
            escapeCSV(item.question),
            escapeCSV(item.optionA),
            escapeCSV(item.optionB),
            escapeCSV(item.optionC),
            escapeCSV(item.optionD),
            escapeCSV(item.correctAnswer),
            escapeCSV(item.playerAnswer),
            escapeCSV(item.timestamp)
        ].join(',');
        csvContent += row + '\n';
    });

    // 使用 data URI 方式下载（兼容 file:// 协议）
    const BOM = '\uFEFF';  // UTF-8 BOM 确保 Excel 正确识别中文
    const csvData = BOM + csvContent;

    // 使用 Base64 编码
    const base64 = btoa(unescape(encodeURIComponent(csvData)));
    const dataUri = 'data:text/csv;charset=utf-8;base64,' + base64;

    // 创建下载链接
    const link = document.createElement('a');
    link.href = dataUri;
    link.download = '错题本.csv';

    // 触发下载
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    console.log('错题本下载完成，共' + wrongBook.length + '道题');
}

// 清空错题本（可选功能）
function clearWrongBook() {
    if (confirm('确定要清空错题本吗？此操作不可恢复！')) {
        localStorage.removeItem(WRONG_BOOK_KEY);
        alert('错题本已清空！');
    }
}
