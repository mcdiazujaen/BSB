export PATH=/usr/local/bin:$PATH
export LD_LIBRARY_PATH=/opt/FreeLing-4.0/src/libfreeling/:/usr/local/lib/:$LD_LIBRARY_PATH

HOME=$(pwd)

cd $1
mkdir naf

for file in *;
do
    if [ -f $file ]; then
	analyze -f /usr/local/share/freeling/config/es.cfg < $file > $file.naf --output naf
	perl $HOME/search_freeling_med/naf++.pl $file.naf $file.etkt.naf
	mv $file.etkt.naf naf/$file.etkt.naf;
	rm $file.naf
    fi
done
