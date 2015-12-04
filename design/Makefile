docx:
	@pandoc -f markdown -t docx -o design.docx design.md

wiki:
	@pandoc -f markdown -t mediawiki -o design.wiki design.md

all: docx wiki

clean:
	rm -f design.docx design.wiki

.PHONY: docx wiki clean
