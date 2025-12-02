class SentenceBuffer:

	def __init__(self, delimiters: str = "。！？!?") -> None:
		self._buffer = ""
		self._delimiters = delimiters

	def add_text(self, text: str) -> list[str]:
		if not text:
			return []
		self._buffer += text
		sentences: list[str] = []
		start = 0
		for i, ch in enumerate(self._buffer):
			if ch in self._delimiters:
				segment = self._buffer[start : i + 1].strip()
				if segment:
					sentences.append(segment)
				start = i + 1
		self._buffer = self._buffer[start:]
		return sentences

	def flush_rest(self) -> str:
		rest = self._buffer.strip()
		self._buffer = ""
		return rest
