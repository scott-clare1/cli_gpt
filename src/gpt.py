import os
from playwright.sync_api import sync_playwright
import json
from rich.console import Console
from rich.markdown import Markdown
import html2text

converter = html2text.HTML2Text()
console = Console()

class GPT:

	def __init__(self, p):
		self.p = p

		self.browser = None
		self.context = None
		self.page = None
		self.cookies_path = f"{os.path.dirname(os.path.abspath(__file__))}/cookies.json"
		self.cookies = None if not self.cookies_exist() else self._load_cookies()
		self.conversation_turn = 3

	def connect(self, headless):
		self.browser = self.p.firefox.launch(headless=headless)
		self.context = self.browser.new_context()
		self.page = self.context.new_page()
	
	def cookies_exist(self):
		return os.path.exists(self.cookies_path)

	def _get_cookies(self):
		return self.context.cookies()
	
	def _save_cookies(self):
		cookies = self._get_cookies()	
		with open(self.cookies_path, "w") as f:
			json.dump(cookies, f)

	def _load_cookies(self):
		with open(self.cookies_path, "r") as f:
			cookies = json.load(f)
		return cookies

	def add_cookies(self):
		self.context.add_cookies(self.cookies)

	def login(self):
		self.connect(headless=False)
		self.page.goto("https://chat.openai.com/")
	
	def reload(self):
		self.connect(headless=True)
		self.add_cookies()
		self.page.goto("https://chat.openai.com/")
#		try:
#			page.wait_for_selector('#prompt-textarea')
#		except Exception as e:
#			print("Page no loaded properly - are you sure you signed in correctly before processing Enter?")
#			self.close()
#			os.remove(self.cookies_path)
	@staticmethod
	def _convert_to_markdown(html):
		return converter.handle(html)		


	@staticmethod
	def save_markdown(html):
		markdown_content = self._convert_to_markdown(html)

	def query(self, prompt):
		self.page.fill(f"textarea#prompt-textarea", prompt)
		self.page.click('[data-testid="send-button"]')
		self.page.wait_for_load_state('networkidle')
		import time
		time.sleep(5)
		elements = self.page.query_selector_all(f'[data-testid="conversation-turn-{self.conversation_turn}"]')
		for element in elements:
			html_content = self.page.evaluate('(element) => element.outerHTML', element)
			console.print(Markdown(self._convert_to_markdown(html_content)))
		self.conversation_turn += 2
	
	def close(self):
		self._save_cookies()		
		self.context.close()		
		self.browser.close()

def main():
	with sync_playwright() as p:
		gpt = GPT(p)
		if not gpt.cookies:
			gpt.login()
			print("Press Enter once logged in")
			x = input()
			if not x: 			
				gpt.close()			
		gpt.reload()
		while True:
			print("Enter query")
			prompt = input()
			if prompt == "exit()":
				print("Terminating...")
				break
			gpt.query(prompt)

		gpt.close()


if __name__ == "__main__":
	main()
