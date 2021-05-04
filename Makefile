.PHONY: thesis.pdf release clean

thesis.pdf:
	latexmk -pdf thesis.tex

release: thesis.pdf
	mkdir -p releases
	cp --no-clobber thesis.pdf releases/thesis-"$$(date '+%F')"-"$$(git describe --always --dirty)".pdf

clean:
	latexmk -C
