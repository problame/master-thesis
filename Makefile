.PHONY: thesis.pdf clean

thesis.pdf:
	latexmk -pdf thesis.tex

clean:
	latexmk -C
