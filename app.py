import ast
import math
import operator

import streamlit as st


BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
EXAMPLES = ["18 * 6 + 12", "100 / 4", "50 - 17", "7 * 9"]


def calc(expression):
    if len(expression) > 200:
        raise ValueError("Keep expressions under 200 characters.")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError("Enter a valid arithmetic expression.") from error

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponents must be between -100 and 100.")
            result = BINARY_OPERATORS[type(node.op)](left, right)
            if isinstance(result, float) and not math.isfinite(result):
                raise ValueError("The result is too large to display.")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
            return UNARY_OPERATORS[type(node.op)](evaluate(node.operand))
        raise ValueError("Use numbers and the operators +, -, *, /, //, %, and **.")

    return evaluate(tree)


def load_example():
    st.session_state.expression = st.session_state.example


def format_result(value):
    if isinstance(value, float):
        return f"{value:,.12g}"
    return f"{value:,}"


st.set_page_config(page_title="Calculator", page_icon="+", layout="centered")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root {
        --ink: #172b2b;
        --muted: #657676;
        --paper: #f3f7f5;
        --line: #d9e4df;
        --teal: #087e72;
        --coral: #e36f54;
    }
    .stApp { background: var(--paper); color: var(--ink); }
    .block-container { max-width: 820px; padding-top: 4rem; }
    html, body, [class*="st-"] { font-family: 'Manrope', sans-serif; }
    h1 { color: var(--ink); font-weight: 800; letter-spacing: 0; }
    .eyebrow {
        color: var(--teal); font-family: 'DM Mono', monospace;
        font-size: 0.75rem; font-weight: 500; margin-bottom: 0.75rem;
    }
    .stCaption { color: var(--muted); }
    div[data-testid="stForm"] {
        background: #ffffff; border: 1px solid var(--line);
        border-radius: 8px; padding: 1.25rem;
    }
    div[data-testid="stTextInput"] input {
        font-family: 'DM Mono', monospace; font-size: 1.05rem;
    }
    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label { color: var(--muted); }
    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background: var(--teal); color: white; border: 0; border-radius: 5px;
        font-weight: 700; min-height: 2.8rem;
    }
    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #06685f; color: white; border: 0;
    }
    div[data-testid="stMetric"] {
        background: #e2efea; border-left: 4px solid var(--coral);
        border-radius: 4px; padding: 1.2rem 1.3rem;
    }
    div[data-testid="stMetricValue"] {
        color: var(--ink); font-family: 'DM Mono', monospace; font-size: 2rem;
    }
    code { color: var(--teal); }
    @media (max-width: 640px) {
        .block-container { padding-top: 2rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">NUMBER WORKSHOP  /  01</div>', unsafe_allow_html=True)
st.title("Calculator")
st.caption("A clear space for quick arithmetic.")

if "expression" not in st.session_state:
    st.session_state.expression = "18 * 6 + 12"
if "answer" not in st.session_state:
    st.session_state.answer = None
if "error" not in st.session_state:
    st.session_state.error = None

input_column, result_column = st.columns([1.2, 0.8], gap="large")

with input_column:
    st.selectbox(
        "Examples",
        options=EXAMPLES,
        index=None,
        placeholder="Choose an example",
        key="example",
        on_change=load_example,
    )
    with st.form("calculator_form"):
        st.text_input("Expression", key="expression", placeholder="e.g. (12 + 8) * 3")
        submitted = st.form_submit_button("Calculate", use_container_width=True)

if submitted:
    try:
        st.session_state.answer = calc(st.session_state.expression)
        st.session_state.error = None
    except (ValueError, ZeroDivisionError, OverflowError) as error:
        st.session_state.answer = None
        st.session_state.error = str(error) or "That expression could not be calculated."

with result_column:
    st.markdown("#### Result")
    if st.session_state.error:
        st.error(st.session_state.error)
    elif st.session_state.answer is not None:
        st.metric("Answer", format_result(st.session_state.answer))
        st.code(st.session_state.expression, language="text")
    else:
        st.metric("Answer", "--")