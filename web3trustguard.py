import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
MCP_URL = os.getenv("MCP_URL")
API_BASE = os.getenv("API_BASE")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")


class Web3ClassicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web3 Trust Guard - MCP UI by Bolaji M.L")
        self.root.geometry("1300x820")
        self.root.resizable(True, True)
        self.total_tokens_used = 0

        # Canvas for vertical scrolling
        canvas = tk.Canvas(self.root, bg="#d0d8e8")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside canvas
        self.scroll_frame = tk.Frame(canvas, bg="#d0d8e8")
        self.scroll_window = canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')

        def on_canvas_resize(event):
            canvas.itemconfig(self.scroll_window, width=event.width)

        canvas.bind("<Configure>", on_canvas_resize)

        # Update scroll region when resized
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_resize(event):
            canvas.itemconfig(self.scroll_window, width=event.width)

        self.scroll_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_resize)

        self.tools = self.fetch_tools()
        self.build_interface()


    def build_interface(self):
        tk.Label(self.scroll_frame, text="WEB3 TRUST GUARD MCP SERVER - BY BOLAJI ML",
                 font=("Segoe UI", 16, "bold"), bg="#26476b", fg="white", pady=10).pack(fill="x")

        # --- Top 3-column row ---
        top_frame = tk.Frame(self.scroll_frame, bg="#c7d0e0")
        top_frame.pack(fill="x", padx=10, pady=5)

        # Analysis Request
        analysis_frame = tk.LabelFrame(top_frame, text="Analysis Request", font=("Segoe UI", 10, "bold"),
                                       bg="#e6edf7", padx=7, pady=7)
        analysis_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.query_entry = tk.Text(analysis_frame, height=2, font=("Segoe UI", 10))
        self.query_entry.pack(fill="x", pady=5)

        btn_frame = tk.Frame(analysis_frame, bg="#e6edf7")
        btn_frame.pack()
        tk.Button(btn_frame, text="Run Analysis", font=("Segoe UI", 9), bg="#26476b", fg="white",
                  command=self.process_query).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Clear All", font=("Segoe UI", 9), bg="#a94442", fg="white",
                  command=self.clear_all).pack(side="left", padx=3)

        # Prompt Examples
        example_frame = tk.LabelFrame(top_frame, text="Prompt Examples", font=("Segoe UI", 10, "bold"),
                                      bg="#f0f4ff", padx=8, pady=5)
        example_frame.pack(side="left", fill="both", expand=True, padx=5)

        examples = [
            "Check token 0x880bce9321c79cac1d290de6d31dde722c606165 on BNB",
            "NFT ID 1 from contract 0xee24b9872022c7770CCC828d856224416CBa005f",
            "Check if https://noblepci.com/innovation is phishing",
        ]
        for prompt in examples:
            btn = tk.Button(example_frame, text=prompt, anchor="w", font=("Segoe UI", 9),
                            wraplength=220, justify="left", bg="#edf2fc", relief=tk.RIDGE,
                            command=lambda p=prompt: self.query_entry.delete("1.0", tk.END) or self.query_entry.insert("1.0", p))
            btn.pack(fill="x", pady=1)

        # Available Tools
        tool_frame = tk.LabelFrame(top_frame, text="Available Tools", font=("Segoe UI", 10, "bold"),
                                   bg="#e6edf7", padx=10, pady=10)
        tool_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.tool_dropdown = ttk.Combobox(tool_frame,
                                          values=[tool['function']['name'] for tool in self.tools],
                                          state="readonly", width=35)
        self.tool_dropdown.set("See all tools available")
        self.tool_dropdown.pack(pady=5)

        self.token_label = tk.Label(tool_frame, text="Tokens Used: 0",
                                    font=("Segoe UI", 9, "bold"), bg="#e6edf7", fg="#222")
        self.token_label.pack(pady=(10, 0))

        # --- Middle row ---
        mid_frame = tk.Frame(self.scroll_frame, bg="#c7d0e0")
        mid_frame.pack(fill="x", padx=10, pady=5)

        self.tool_box = self.create_output_box(mid_frame, "Tool Detected", height=4, side="left")
        self.payload_box = self.create_output_box(mid_frame, "Payload Sent", height=4, side="left")
        self.raw_response_box = self.create_output_box(mid_frame, "Raw MCP JSON Response", height=12, side="left")

        # --- Bottom row ---
        self.claude_box = self.create_output_box(self.scroll_frame, "AI Agent Explanation (Summary)", height=9)

    def create_output_box(self, parent, title, height=4, side=None):
        frame = tk.LabelFrame(parent, text=title, font=("Segoe UI", 10, "bold"),
                              bg="#f4f6fc", fg="#222", padx=10, pady=5, bd=2, relief=tk.SUNKEN)
        if side:
            frame.pack(side=side, fill="both", expand=True, padx=5, pady=5)
        else:
            frame.pack(fill="both", expand=True, padx=10, pady=5)

        text_widget = tk.Text(frame, height=height, width=50, bg="white", fg="#000",
                              font=("Consolas", 10), wrap="word")
        text_widget.pack(fill="both", expand=True)
        return text_widget

    def fetch_tools(self):
        try:
            res = requests.get(MCP_URL)
            return res.json().get("tools", [])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load MCP tools: {e}")
            return []

    def process_query(self):
        query = self.query_entry.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Missing Input", "Please enter a request.")
            return

        self.clear_all()
        tool, payload, debug_info, tokens_used = self.analyze_query_with_groq(query)
        if tool and payload:
            self.tool_box.insert("1.0", tool)
            self.payload_box.insert("1.0", json.dumps(payload, indent=2))
            self.update_token_usage(tokens_used)
            self.call_tool(tool, payload)
        else:
            self.tool_box.insert("1.0", "Could not determine the correct tool from the query.")

    def analyze_query_with_groq(self, query_text):
        try:
            tool_schemas = [
                {
                    "name": "check_token",
                    "params": {"address": "string", "chain_id": "integer"}
                },
                {
                    "name": "check_wallet",
                    "params": {"address": "string", "chain_id": "integer"}
                },
                {
                    "name": "check_nft",
                    "params": {"contract": "string", "token_id": "string", "chain_id": "integer"}
                },
                {
                    "name": "check_url",
                    "params": {"url": "string"}
                },
                {
                    "name": "simulate_sol_tx",
                    "params": {"tx_base64": "string"}
                },
                {
                    "name": "check_sol_token",
                    "params": {"address": "string"}
                },
                {
                    "name": "verify_donation",
                    "params": {"tx_hash": "string", "chain": "string", "chain_id": "integer (optional)"}
                },
                {
                    "name": "list_verified_causes",
                    "params": {}
                }
            ]

            prompt = (
                "You are a Web3 assistant for a Model Context Protocol (MCP) server."
                " Your task is to extract the correct tool and payload from user queries.\n"
                "ONLY choose from the following tools and use their exact parameter names and types:\n"
                + "\n".join([
                    f"{t['name']}: {json.dumps(t['params'])}" for t in tool_schemas
                ]) + "\n\n"
                "Use ONLY this JSON format:\n"
                "{ \"tool\": \"tool_name\", \"payload\": { valid_key_values } }\n\n"
                "If the query doesn't match any tool, return:\n"
                "{ \"tool\": null, \"payload\": {} }\n\n"
                f"User query:\n\"{query_text}\""
            )

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            }
            body = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0
            }

            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
            res.raise_for_status()
            data = res.json()
            reply = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 500)
            parsed = json.loads(reply)

            tool = parsed.get("tool")
            payload = parsed.get("payload")

            valid_tool_names = [t["name"] for t in tool_schemas]
            if tool not in valid_tool_names:
                return None, None, reply, tokens_used

            return tool, payload, reply, tokens_used

        except Exception as e:
            return None, None, str(e), 0



    def call_tool(self, tool, payload):
        try:
            url = f"{API_BASE}/{tool}/"
            res = requests.post(url, json=payload)
            res.raise_for_status()
            result = res.json()
            self.raw_response_box.insert("1.0", json.dumps(result, indent=2))
            self.ask_groq(tool, result)
        except Exception as e:
            self.raw_response_box.insert("1.0", f"Error: {e}")

    def ask_groq(self, tool_name, raw_json):
        try:
            prompt = (
                f"You are a Web3 assistant. A user ran the tool '{tool_name}' and got this JSON:\n\n"
                f"{json.dumps(raw_json, indent=2)}\n\n"
                "Now summarize the result in a concise, clear bullet-point format. Keep it short.\n"
                "Avoid long paragraphs. Focus on key risks, insights, and actions.\n"
                "Respond only with the summary — no explanations or headers."
            )
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            }
            body = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "temperature": 0.4
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
            res.raise_for_status()
            data = res.json()
            summary = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 600)
            self.update_token_usage(tokens_used)
            self.claude_box.insert("1.0", summary)
        except Exception as e:
            self.claude_box.insert("1.0", f"Groq error: {str(e)}")


    def update_token_usage(self, tokens):
        self.total_tokens_used += tokens
        self.token_label.config(text=f"Tokens Used: {self.total_tokens_used:,}")

    def clear_all(self):
        self.query_entry.delete("1.0", tk.END)
        self.tool_box.delete("1.0", tk.END)
        self.payload_box.delete("1.0", tk.END)
        self.raw_response_box.delete("1.0", tk.END)
        self.claude_box.delete("1.0", tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = Web3ClassicGUI(root)
    root.mainloop()
