import os
import random
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "detective_conan_full_project_key_2026")

# 4대 대표 추리 사건 데이터
CASES = {
    "case_bandaged": {
        "id": "case_bandaged",
        "title": "사건 01. 산장 붕대남 살인사건",
        "theme": "밀실·고립 서스펜스",
        "partner": "에도가와 코난",
        "partner_avatar": "conan_watch.jpg",
        "bg_img": "conan_main.jpg",
        "bgm": "https://ia800301.us.archive.org/15/items/lp_moonlight-sonata_ludwig-van-beethoven-frdric-chopin-alexand/lp_moonlight-sonata_ludwig-van-beethoven-frdric-chopin-alexand_disc1side1.mp3",
        "intro": "폭풍우로 외나무다리가 끊겨 고립된 산장. 붕대로 얼굴을 가린 괴한이 창밖을 맴돌고 별채에서 처참한 살인사건이 일어났습니다. 현장 단서를 수집해 트릭 도구를 조합하세요!",
        "hotspots": [
            {"id": "clue_wire", "name": "창문가 바닥", "desc": "잘려 나간 피아노선 조각과 창틀의 미세한 마찰 홈을 발견했습니다.", "item": "피아노선 조각", "icon": "🎻"},
            {"id": "clue_coat", "name": "벽걸이 옷걸이", "desc": "피 묻은 붕대와 유난히 두툼하게 솜을 채운 외투를 획득했습니다. (체형 위장용)", "item": "두꺼운 외투", "icon": "🧥"},
            {"id": "clue_terrace", "name": "테라스 난간", "desc": "난간 기둥에 빗물에도 지워지지 않은 낚싯줄 마찰 흔적이 남아 있습니다.", "item": "테라스 마찰흔", "icon": "🔍"}
        ],
        "combination": {
            "result": "목 매달기 활차 트릭 도구",
            "desc": "외투 속에 머리를 숨겨 창밖으로 이동한 뒤 피아노선 활차로 시신을 끌어당긴 트릭을 규명했습니다!"
        },
        "suspects": [
            {"id": "s1", "name": "타카하시 료이치 (특수분장)", "role": "뚱뚱한 체형", "alibi": "지붕 수리를 하고 있었으며 체형이 뚱뚱해 좁은 창문을 넘을 수 없다고 주장."},
            {"id": "s2", "name": "오오타 마사루", "role": "배우 지망생", "alibi": "비를 피해 거실 소파에서 란과 대화 중이었다고 진술."},
            {"id": "s3", "name": "카쿠다 히로키", "role": "촬영 스태프", "alibi": "카메라 장비를 챙겨 2층 방으로 일찍 들어갔다고 주장."}
        ],
        "default_choices": [
            "코난! 창문 틈에 걸린 피아노선 조각은 대체 어디에 쓴 거지?",
            "타카하시 씨의 뚱뚱한 체형이 사실 솜과 외투로 위장한 거 아닐까?",
            "테라스 난간의 낚싯줄과 창문 와이어를 연결하면 시신을 공중으로 날릴 수 있어!"
        ],
        "culprit_id": "s1",
        "solution": "진범 타카하시는 솜을 넣은 두꺼운 외투로 체형을 위장하고, 피아노선 활차를 이용해 시신을 운반했습니다. '뚱뚱해서 창틀을 넘을 수 없다'는 알리바이를 역이용한 지능적 트릭이었습니다."
    },
    "case_moonlight": {
        "id": "case_moonlight",
        "title": "사건 02. 월광 소나타 살인사건",
        "theme": "음악·다잉 메시지 암호",
        "partner": "에도가와 코난",
        "partner_avatar": "conan_pointing.jpg",
        "bg_img": "conan_pointing.jpg",
        "bgm": "https://ia800301.us.archive.org/15/items/lp_moonlight-sonata_ludwig-van-beethoven-frdric-chopin-alexand/lp_moonlight-sonata_ludwig-van-beethoven-frdric-chopin-alexand_disc1side1.mp3",
        "intro": "달빛 비치는 월영도 공민관. 베토벤의 '월광' 선율 뒤에 살인사건이 발생했습니다. 현장에 남겨진 피 묻은 악보 속 알파벳 암호를 풀어내세요!",
        "hotspots": [
            {"id": "clue_sheet", "name": "피아노 건반 덮개", "desc": "건반 밑에 숨겨진 피 묻은 악보 조각 발견! 음표 아래에 암호 점이 찍혀 있습니다.", "item": "피 묻은 악보", "icon": "🎼"},
            {"id": "clue_tape", "name": "카세트 오디오", "desc": "자동 반복 재생 테이프로 월광 소나타가 스스로 울려 퍼지게 만든 트릭 확인!", "item": "녹음 테이프", "icon": "📼"},
            {"id": "clue_table", "name": "음표 암호 대조표", "desc": "건반의 음계 순서대로 알파벳 A부터 Z까지 일대일 대응되는 규칙을 발견했습니다.", "item": "음계 암호표", "icon": "📜"}
        ],
        "suspects": [
            {"id": "s1", "name": "아사이 나루미 (여의사)", "role": "섬의 진료소 의사", "alibi": "공민관 밖에서 시신 검시를 준비하고 있었다고 진술."},
            {"id": "s2", "name": "시미즈 마사토", "role": "촌장 후보", "alibi": "선거 유세 회의실에서 참모들과 투표 전략 회의 중이었다고 주장."},
            {"id": "s3", "name": "무라사와 슈이치", "role": "피아노 조율사", "alibi": "창고에서 부품을 찾느라 연주 소리를 전혀 듣지 못했다고 증언."}
        ],
        "default_choices": [
            "악보의 음표들을 피아노 건반 순서(A=도, B=레...)로 변환해보자!",
            "카세트 테이프가 돌아간 시간에 범인은 다른 곳에 있었던 것처럼 속였어.",
            "아사이 선생님의 과거와 12년 전 피아니스트 아소 케이지 사건이 연결돼 있어!"
        ],
        "culprit_id": "s1",
        "solution": "피아노 건반에 새겨진 악보 암호의 해독 결과는 'ASAI(아사이)'였습니다. 의사 아사이 나루미는 12년 전 억울하게 희생된 피아니스트 아버지의 복수를 위해 악보 다잉 메시지를 남겼던 것입니다."
    },
    "case_kid": {
        "id": "case_kid",
        "title": "사건 03. 괴도 키드의 순백의 공중보행",
        "theme": "도난 방지·착시 트릭",
        "partner": "에도가와 코난",
        "partner_avatar": "conan_watch.jpg",
        "bg_img": "conan_main.jpg",
        "bgm": "https://ia800301.us.archive.org/15/items/lp_moonlight-sonata_ludwig-van-beethoven-frdric-chopin-alexand/lp_moonlight-sonata_ludwig-van-beethoven-frdric-chopin-alexand_disc1side1.mp3",
        "intro": "자정 정각, 고층 빌딩 상공에서 보석 '블루 미라클'을 훔치겠다는 괴도 키드의 예고장! 허공을 걷는 공중보행 착시 트릭을 밝혀내세요.",
        "hotspots": [
            {"id": "clue_card", "name": "괴도 키드의 카드", "desc": "'달이 두 개의 탑 사이에 걸릴 때, 나는 밤하늘을 걸어 내려온다.'", "item": "예고장 카드", "icon": "🃏"},
            {"id": "clue_crane", "name": "옥상 크레인 도르래", "desc": "헬리콥터 와이어와 연결된 특수 극세사 와이어 및 원격 권양기 장치 발견!", "item": "극세사 와이어", "icon": "⚙️"},
            {"id": "clue_cam", "name": "감시 카메라 착시 렌즈", "desc": "관중들의 시야각과 프로젝터 반사판 각도가 정밀하게 계산되어 있습니다.", "item": "착시 계산 메모", "icon": "📐"}
        ],
        "suspects": [
            {"id": "s1", "name": "괴도 키드 (변장)", "role": "월하의 마술사", "alibi": "밤하늘 상공에서 관중들을 향해 손을 흔들고 있음."},
            {"id": "s2", "name": "스즈키 지로키치", "role": "전시관 고문", "alibi": "박물관 출입구를 완전 봉쇄하고 지휘 중이었다고 주장."},
            {"id": "s3", "name": "헬기 조종사", "role": "경찰 항공대", "alibi": "상공에서 순찰 비행 중이었으며 키드의 동조자가 아니라고 진술."}
        ],
        "default_choices": [
            "키드가 하늘을 걷는 게 아니라 헬기 2대 사이에 친 와이어에 매달려 있는 거야!",
            "서치라이트를 순서대로 비춰서 밤하늘의 투명 와이어 그림자를 폭로하자!",
            "헬기 조종사 중에 키드의 조수가 섞여 있어!"
        ],
        "culprit_id": "s1",
        "solution": "키드는 헬기에서 늘어뜨린 특수 와이어와 도르래로 체중을 지탱하며 허공을 걷는 흉내를 냈습니다. 서치라이트로 와이어의 그림자를 드러내자 트릭이 파훼되었습니다."
    },
    "case_train": {
        "id": "case_train",
        "title": "사건 04. 칠흑의 미스터리 트레인 & 검은 조직",
        "theme": "탈출·스릴러",
        "partner": "아카이 슈이치 (FBI)",
        "partner_avatar": "akai_shuichi.jpg",
        "bg_img": "akai_shuichi.jpg",
        "bgm": "https://ia800301.us.archive.org/15/items/lp_moonlight-sonata_ludwig-van-beethoven-frdric-chopin-alexand/lp_moonlight-sonata_ludwig-van-beethoven-frdric-chopin-alexand_disc1side1.mp3",
        "intro": "벨트리 급행 열차에 침투한 검은 조직의 진, 워커, 버번! 화물칸 폭파 카운트다운(60초)이 시작되었습니다. 객차를 분리하고 안전하게 탈출시키세요!",
        "hotspots": [
            {"id": "clue_bomb", "name": "화물칸 폭탄 박스", "desc": "C4 시한폭약과 C-7 연결 해제용 키패드가 노출되어 있습니다!", "item": "연결 해제 키패드", "icon": "💣"},
            {"id": "clue_ticket", "name": "1등석 승차권 티켓", "desc": "승차권 뒷면에 적힌 특수 객차 분리 코드 메모: '8942'", "item": "분리 코드 메모", "icon": "🎟️"},
            {"id": "clue_vent", "name": "환기구 연막탄 잔해", "desc": "괴도 키드가 협력용으로 남겨둔 특수 변장 마스크 조각을 획득했습니다.", "item": "키드의 연막탄", "icon": "🎭"}
        ],
        "suspects": [
            {"id": "s1", "name": "아무로 토오루 (버번)", "role": "조직의 정보원", "alibi": "화물칸 통로를 가로막고 쉐리를 추궁 중."},
            {"id": "s2", "name": "수수께끼의 승객", "role": "열차 승객", "alibi": "객실 복도를 배회 중."},
            {"id": "s3", "name": "진 & 워커 (검은 조직)", "role": "나고야 역 대기", "alibi": "열차가 역에 진입하는 순간 화물칸을 통째로 폭파하려 함."}
        ],
        "default_choices": [
            "슈이치 씨! 승차권에 적힌 암호 '8942'를 패드에 입력해 객차를 떼어내야 해요!",
            "화물칸 안에 있는 쉐리는 사실 키드가 변장한 대역이야!",
            "버번이 눈치채기 전에 폭탄이 터지는 연결 부위를 끊고 수류탄으로 위장하자!"
        ],
        "culprit_id": "s3",
        "solution": "승차권 비밀번호 '8942'로 화물칸을 안전하게 분리하고, 키드가 쉐리로 변장한 뒤 행글라이더로 공중 탈출에 성공하여 검은 조직의 암살 계획을 완벽히 무산시켰습니다."
    }
}

LEGACY_MAP = {
    "case_1": "case_bandaged",
    "case_2": "case_moonlight",
    "case_3": "case_kid",
    "case_4": "case_train"
}

# 오늘의 탐정 운세 데이터
FORTUNES = {
    "success": [
        {
            "luck": "대길 (大吉) - 실버 불렛(은빛 탄환)의 직관",
            "phrase": "“추리에 이기고 지는 건 없어. 진실은 언제나 단 하나뿐이니까!” 오늘 당신의 모든 결정과 판단은 과녁의 한가운데를 정확히 꿰뚫습니다.",
            "color": "파란색",
            "item": "코난의 붉은 나비넥타이 음성변조기"
        },
        {
            "luck": "상길 (上吉) - 월하의 마술사를 간파한 혜안",
            "phrase": "“트릭은 뇌가 만들어낸 수수께끼일 뿐이야.” 복잡하게 꼬여 있던 문제의 실마리가 오늘 거짓말처럼 명쾌하게 풀려나갑니다.",
            "color": "흰색",
            "item": "괴도 키드의 모노클 안경"
        }
    ],
    "fail": [
        {
            "luck": "중길 (中吉) - 빗나간 마취총과 재도약의 시간",
            "phrase": "“완벽한 인간은 없어. 실패를 딛고 일어설 때 비로소 진짜 탐정이 되는 거야.” 성급함을 가라앉히고 한 템포 쉬어가면 뜻밖의 조력자를 만납니다.",
            "color": "초록색",
            "item": "아가사 박사표 따뜻한 레몬 홍차"
        },
        {
            "luck": "소길 (小吉) - 안개 낀 런던의 신중함",
            "phrase": "“눈앞의 환상에 속지 마라. 보이지 않는 곳에 진짜 열쇠가 있다.” 서두르지 말고 단서들의 연결고리를 차분히 재점검해보세요.",
            "color": "검은색",
            "item": "아카이 슈이치의 검은 니트 비니"
        }
    ]
}

@app.route("/")
def index():
    return render_template("index.html", cases=CASES)

@app.route("/case/<case_id>")
def case_detail(case_id):
    if case_id in LEGACY_MAP:
        return redirect(url_for('case_detail', case_id=LEGACY_MAP[case_id]))

    case = CASES.get(case_id)
    if not case:
        return redirect(url_for('case_detail', case_id='case_bandaged'))

    session["current_case"] = case_id
    user_api_key = session.get("user_openai_api_key", "")
    return render_template("sub.html", case=case, user_api_key=user_api_key)

# 사용자 개인 API 키 등록 라우트
@app.route("/api/set_key", methods=["POST"])
def set_key():
    data = request.get_json()
    key = data.get("api_key", "").strip()
    session["user_openai_api_key"] = key
    return jsonify({"status": "ok", "saved": bool(key)})

@app.route("/solve", methods=["POST"])
def solve():
    case_id = request.form.get("case_id")
    chosen = request.form.get("suspect")
    case = CASES.get(case_id, CASES["case_bandaged"])
    
    is_correct = (chosen == case["culprit_id"])
    pool = FORTUNES["success"] if is_correct else FORTUNES["fail"]
    fortune = random.choice(pool)
    
    return render_template("result.html", case=case, is_correct=is_correct, fortune=fortune)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    
    user_api_key = session.get("user_openai_api_key") or data.get("api_key", "").strip()
    
    if not user_api_key:
        return jsonify({
            "reply": "⚠️ 우측 상단의 '🔑 내 OpenAI API 키' 입력창에 본인의 API 키(sk-...)를 먼저 입력해줘! 그래야 나와 실시간으로 수사를 공조할 수 있어!"
        })

    case_id = session.get("current_case", "case_bandaged")
    case = CASES.get(case_id, CASES["case_bandaged"])
    
    system_prompt = (
        f"당신은 명탐정 코난 원작 속의 '{case['partner']}'입니다. "
        f"현재 플레이어와 함께 [{case['title']}] 현장에서 긴박하게 추리 중입니다.\n"
        f"사건 단서: {', '.join([h['name'] + ' - ' + h['desc'] for h in case['hotspots']])}\n"
        f"정답 진범 ID: {case['culprit_id']}\n"
        f"규칙:\n"
        f"1. 범인의 정답 이름을 절대로 직접 발설하지 마세요.\n"
        f"2. {case['partner']} 특유의 성격과 말투(코난은 '어레레~? 이상하네?', '바보야, 그게 아니잖아!', 아카이는 '당황하지 마라, 런(Run)...')를 100% 살리세요.\n"
        f"3. 2~3문장 이내로 플레이어가 단서를 조합하거나 암호를 풀 수 있도록 날카로운 힌트를 건네세요."
    )
    
    try:
        user_client = OpenAI(api_key=user_api_key)
        res = user_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=250
        )
        return jsonify({"reply": res.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": "입력하신 OpenAI API 키가 유효하지 않거나 사용 한도를 초과했어! 키를 다시 확인해줘."})

if __name__ == "__main__":
    # Render 클라우드 환경의 포트 바인딩 및 로컬 지원
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)