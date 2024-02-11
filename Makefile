archive_name=xtesar43.zip
testdir=testdir

default: test pack

pack:
	zip $(archive_name) parse.py readme1.md rozsireni
	mkdir -p $(testdir)
	./is_it_ok.sh $(archive_name) $(testdir) --force

test:
	cd tests/supplementary-tests/parse && make

clean:
	rm -f $(archive_name) *.log
	rm -rf $(testdir)
