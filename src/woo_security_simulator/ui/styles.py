"""Minimal responsive styling with no remote assets."""

import streamlit as st

CSS = """
<style>
:root {
  --northstar-ink: var(--text-color);
  --northstar-muted: var(--text-color);
  --northstar-surface: var(--secondary-background-color);
  --northstar-border: color-mix(
    in srgb,
    var(--text-color) 24%,
    var(--background-color)
  );
  --northstar-accent: var(--primary-color);
}
[data-testid="stSidebar"] { border-right: 1px solid var(--northstar-border); }
.simulator-badge {
  display: inline-block;
  padding: .3rem .65rem;
  border-radius: 999px;
  background: var(--northstar-surface);
  color: var(--northstar-ink);
  border: 1px solid var(--northstar-accent);
  font-weight: 700;
  font-size: .85rem;
  margin-bottom: .75rem;
}
.product-art {
  min-height: 7rem;
  border-radius: .75rem;
  display: grid;
  place-items: center;
  background: linear-gradient(
    145deg,
    var(--northstar-surface),
    var(--background-color)
  );
  color: var(--northstar-ink);
  border: 1px solid var(--northstar-border);
  font-size: 2.5rem;
}
.price-total {
  padding: .9rem 1rem;
  border-radius: .65rem;
  background: var(--northstar-surface);
  color: var(--northstar-ink);
  border: 1px solid var(--northstar-border);
}
@media (max-width: 640px) {
  h1 { font-size: 1.8rem !important; }
  h2 { font-size: 1.4rem !important; }
  .block-container { padding: 1rem .8rem 3rem; }
  .product-art { min-height: 5rem; }
}
</style>
"""


def apply_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
