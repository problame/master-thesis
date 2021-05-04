.PHONY: thesis.pdf release clean

thesis.pdf:
	latexmk -pdf thesis.tex

release: thesis.pdf
	mkdir -p releases
	if git describe --always --dirty | grep dirty ; then echo must not be dirty; exit 1; fi
	releasename="$$(date '+%F')"-"$$(git describe --always --dirty)"; \
		releasefile="releases/thesis-"$$releasename".pdf"; \
		cp --no-clobber thesis.pdf $$releasefile  && \
		git add $$releasefile && \
		git commit -m "release $$releasename"


clean:
	latexmk -C
