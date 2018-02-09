
use XML::LibXML;
use XML::LibXML::Reader;
use XML::Writer;
#use IO;

use strict;
use Data::Dumper;
use File::Temp;
use IPC::Open3;
use IO::Select;
use Symbol;

my %hash_bat;
my $ref_bat=\%hash_bat;
my %hash_bi;
my $ref_bi=\%hash_bi;
my %hash_hiru;
my $ref_hiru=\%hash_hiru;

my %hash_baliokide;
my $ref_baliok=\%hash_baliokide;

my %kategoriak;
my %sustantziak;
my $ref_kategoriak=\%kategoriak;
my $ref_katSust=\%sustantziak;

my $emaitza;

#my $ODOC = XML::LibXML::Document->new('1.0',"UTF-8");

#NAF fitxategia sortu ordez argumentu bezala kargatu eta irakurtzen da
my $reader = XML::LibXML::Reader->new(location => $ARGV[0]) or die "cannot read $ARGV[0]\n";

while ($reader->read) {
    processNode($reader);
}

sub processNode {
    my $reader = shift;
    $reader->preserveNode();
}

#Dokumentu bezala erabiltzen jarraitzeko moldatzen da
my $ODOC = $reader->document();

&KafOsatu;

#NAF aberastua argumentu bezala emandako izenarekin gordetzen da
$ODOC->toFile($ARGV[1], "NAF");

#process_doc barruan, hitzen kopurua lortzeko.
#my $off=0;
#$off= $off + length($par);

########################################################### AZPIPROGRAMAK ######################################################################
	


sub pathak_lortu{

my $hizkuntza=shift;

#my $luzap=".konf";
#MaiteOr-ek aldatua: kategoriak markatzen dituen konfigurazio-fitxategi bertsioak "Kat" du atzetik. Adibidez, SpaKat.txt
my $hizk= $hizkuntza . "Kat";
my $fitx= $hizk . ".konf";
my $katalogoa="/usr/local/share/freeling/es_med/Configuration/";
my $fitxategia=$katalogoa.$fitx;
my @pathak;
	open(FITX,$fitxategia)||die("Ezin da $fitxategia fitxategia zabaldu. \n");
	my $lerro;
        while($lerro=<FITX>){
	my @zatiak= split(/\:/,$lerro);
	my $path=$zatiak[1];
        push(@pathak,$path);
        }



close(FITX);
return @pathak;
}



#<------------------------------------------------- SCT-UMLS baliokidetasunen hasha kargatu ----------------------------------------------------------->#
sub kargatu_sct_umls{

#Parametro bezala pasatako balioak jaso
    my $fitx_in=shift;
    my $baliokidetasun_hash= shift();

    my $lerro;
    my @zutabeak;

    my $kontzeptua;
    my @hitzak;
    my $sct;
    my $cui;
    my @balioak;

#print("\n<---------------  SCT-UMLS baliokidetasunen Hasha kargatzen... ---------------->\n\n");

open(FITX,$fitx_in)|| die("Ezin da $fitx_in fitxategia zabaldu. \n");
binmode(FITX, ":utf8");
	while($lerro=<FITX>){
	    chomp($lerro);
	    @zutabeak=split(/\t/,$lerro);
	   
	    $cui=$zutabeak[0];
	    $sct=$zutabeak[1];
	   

	    if (exists($baliokidetasun_hash->{$sct})){
		#Snomed CT kode hori iadanik hash taulan badago, begiratu eaUMLS kode hori gako horren baliotako bat den
		
		my $aurk=0;
	    	 
	       foreach my $bal (@{$baliokidetasun_hash->{$sct}})
	       {
	         if ($bal eq $cui)
		 {  
		  $aurk=1;
                 }
	       }		

		if ($aurk==0){
		    push(@{$baliokidetasun_hash->{$sct}}, $cui);
		}
	    }
	    else {
		    
		 push(@{$baliokidetasun_hash->{$sct}}, $cui);
		}
	}
}




#<------------------------------------------------- SCT-UMLS baliokidetasunen hasha kargatu ----------------------------------------------------------->#
sub kargatu_ATC{

#Parametro bezala pasatako balioak jaso
    my $fitx_in=shift;
    my $sustantzia_hash= shift;

    my $lerro;
    my @zutabeak;

    my $sust;

#print("\n<---------------  ATCko sustantzien Hasha kargatzen... ---------------->\n\n");

open(FITX2,$fitx_in)|| die("Ezin da $fitx_in fitxategia zabaldu. \n");
binmode(FITX2, ":utf8");
while($lerro=<FITX2>){
    chomp($lerro);
    @zutabeak=split(/\s+/,$lerro);
    $sust=$zutabeak[1]; 
    $sust =~ s/ //g;

    if (!(exists($sustantzia_hash->{$sust}))) # Fomra pluralean eta singularrean dagoenez, lema bera izan dezakegu
	{  
	    $sustantzia_hash->{$sust}= 1;
	}

}
    close(FITX2);
}



#<------------------------------------------------- Kargatu Hashak ------------------------------------------------------------------------->#
sub kargatu_hashak {

my $fitx_descr=shift;
my $ref_bat=shift;
my $ref_bi=shift;
my $href=shift;

#print("\n<-----------------  Snomed CT kontzeptuen Hashak kargatzen... ----------------->\n\n");


open(FITX,$fitx_descr)|| die("Ezin da $fitx_descr fitxategia zabaldu. \n");
binmode(FITX, ":utf8");
my $lerro=<FITX>;
while($lerro=<FITX>){
    chomp($lerro);
    my  @zutabeak=split(/\t/,$lerro);
    my $kod=$zutabeak[0];
    my $azter_kontz=$zutabeak[1];
    #my $kontzeptua=kontzeptua_aztertu($azter_kontz);
    my $kontzeptua=$azter_kontz;

    my @hitzak=split(/\s+/, $azter_kontz);

    my $kop=scalar(@hitzak);
    if(($kop>=1)&&($kop<=2))
    {
	kontzeptua_kargatu($kontzeptua,$kod,$ref_bat);
    }
    elsif (($kop>=3)&&($kop<=4))
    {
        kontzeptua_kargatu($kontzeptua,$kod,$ref_bi);
    }
    else
    {
       
        kontzeptua_kargatu($kontzeptua,$kod,$href);
    }
}

}



sub kontzeptua_kargatu{
    my $kontz= shift();
    my $kod=shift();
    my $hash_laguntzailea =shift();
    my @sct_kodk;
    my $aurk=0;
    
   
    if (exists($hash_laguntzailea->{$kontz})){
#Hash laguntzaileako kontzeptu horren lehen hitzak, "kop" hori duen begiratu
	
	@sct_kodk=@{$hash_laguntzailea->{$kontz}};


	my $i=0;
	while (($i <= $#sct_kodk)&&($aurk==0)){
	    if($sct_kodk[$i]== $kod)
	    {
		$aurk=1;
	    }
	    else
	    {
		$i++;
	    }
	}

	if($aurk==0){
	    push(@sct_kodk,$kod);
	    $hash_laguntzailea->{$kontz}= \@sct_kodk;
	}


}
else
{
   my @sct_kodk1;
    push(@sct_kodk1,$kod);   
   # print("\n\n@sct_kodk ");
    $hash_laguntzailea->{$kontz}= \@sct_kodk1;
}
}

#MaiteOr-ek gehitua
#<------------------------------------------------- Kargatu Kategoriak ------------------------------------------------------------------------->#
# Hash batean kontzeptu bakoitzari dagozkion kategoriak jasoko dira
sub kargatu_kategoriak {

my $fitx_descr=shift;
my $kategoriakB=shift;

# Kontuz!!! Erreferentzia vs Hash-a


#print("\n<-----------------  Snomed CT kontzeptuen Kategoriak Hashan kargatzen... ----------------->\n\n");


open(FITX,$fitx_descr)|| die("Ezin da SFNdunen fitxategia zabaldu. \n");
binmode(FITX, ":utf8");


my $lerro=<FITX>;
while($lerro=<FITX>){
    chomp($lerro);
    my  @zutabeak=split(/\t/,$lerro);
    # ConceptId
    my $SCTid=$zutabeak[0];
    # Kontzeptuaren izena. Azkeneko ()-n bere kategoria dator (producto), (trastorno), (estructura corporal)
    my $azter_kontz=$zutabeak[1];
   
    # kategoria lortu 
    my @zatiak=split(/\(/, $azter_kontz);
  
    my @zatiak2= split(/\)/, $zatiak[$#zatiak]);
    my $kat=$zatiak2[0];
    $kat =~ s/ /_/g;
    
    #print "KONTZEPTUA $SCTid KATEGORIA $kat \n";

    #kargatu hash-a
    if (exists($kategoriakB->{$SCTid}))
	{
	    # gehitu kategoria berri bat soilik eta soilik badlin lehen ez badago...
	    if ($kategoriakB->{$SCTid} !~ /$kat/)
	    {
	    $kategoriakB->{$SCTid} = $kategoriakB->{$SCTid} . "#" . $kat;
	    #print "SCTID= $SCTid KAT=$kategoriakB->{$SCTid}\n"; 
	    }
	}
    else
	{
	    # gehitu kodea eta kategoria berria
	    $kategoriakB->{$SCTid} = $kat;
	}

} # while

}



#<------------------------------------------------------------------ Etiketatzea burutu ----------------------------------------------------------------->#
sub etiketatu {


#my $fname= shift;

my $ref_bat= shift;
my $ref_bi= shift;
my $ref_hiru= shift;
my $ref_baliok=shift;



my $err;

my $root = $ODOC->getDocumentElement;
# Oro
#$ODOC->setEncoding('UTF-8');

 
   my %hash_bilaketak;
    my $aurkitu_hash=\%hash_bilaketak;



#pos atributua, V, G R N daukatenen lemma atributua lortu. ETa zenbakiak? Begiratu ...
foreach my $term_elem ($root->findnodes("//term")) {

#MaiteOr-ek kendua edozein kategoria aztertzeko ...
# MaiteOr-ek berriro ipini du, bestela "gehiegi" etiketatzea gerta liteke
# Orain zeintzuk? N-noun, A-adjetivos, R-adverbios, V-verbos,  ???????????? LMFn desberdin? Ez!
# Zeintzuk ez? D-determinantes, P-pronombres, C-conjunciones, I-interjecciones, S-preposiciones, F-signos de puntuación, Z-cifras y numerales, W-fechas y horas, Q-adjetivos- anticoagulante, analgésico e.a.
my $pos= $term_elem->getAttribute("pos");
if(($pos=~m/^N/)||($pos=~m/^A/)||($pos=~m/^R/)||($pos=~m/^V/) || ($pos=~/^G/))
{
  
#Nagusian kodeak lortu
kodeak_lortu($term_elem,$ref_bat,$ref_bi,$ref_hiru,$ref_baliok,$ref_kategoriak,$ref_katSust);


}
}

return $err;
}


#<-------------------------------------------------------------- Kontzeptu baten kodeak lortu ----------------------------------------------------------->#
sub kodeak_lortu{

my $elem=shift();
my $ref_bat=shift();
my $ref_bi=shift();
my $ref_hiru=shift();
my $hash_baliokide=shift();
my $ref_kategoriak=shift();
my $ref_sustantziak=shift();





my $lemma = $elem->getAttribute("lemma");
my $aurkitu_hash;


#lemma hori descriptions_hash-etan dagoen begiratu
#Lemmaren hitz kopurua kontatu, ze hashetan bilatu behar dugun jakiteko
# MaiteOr: Aztertu: lema "dolor_precordial" bada ("_" azpian duena). Orduan, parekatzea egiten al da?
#Maitek gehitua
$lemma =~ s/\_/ /g;
my @hitzak= split(/\s+/,$lemma);
my $hash_tam=scalar(@hitzak);

if(($hash_tam>=1)&&($hash_tam<=2))
{
    $aurkitu_hash= $ref_bat;
}
elsif (($hash_tam>=3)&&($hash_tam<=4))
{
    $aurkitu_hash= $ref_bi;
}
else
{
    $aurkitu_hash= $ref_hiru;
}

# Sustantziak
#Sustantzia badago ATC zerrendan
#MaiteOr-k gehitua 2013-03-11n
 my ($xrefs) = $elem->findnodes("./externalReferences");
  if(!defined $xrefs) {
    $xrefs = $ODOC->createElement("externalReferences");
    $elem->addChild($xrefs);
  }

if (exists($ref_sustantziak->{$lemma}))
{
    my $xref = $ODOC->createElement("externalRef");
    $xref->setAttribute("resource", "Sust_ATC_2013-03-11");
    $xref->setAttribute("reference", "1");
    $xref->setAttribute("reftype", "Sustantzia_ATC"); 
    $xrefs->addChild($xref);
}


if (exists($aurkitu_hash->{$lemma}))
{
 my @snomed_refs= @{$aurkitu_hash->{$lemma}};

foreach my $sct_id(@snomed_refs){
if(exists($hash_baliokide->{$sct_id}))
{
my @cuis= @{$hash_baliokide->{$sct_id}};

#Baldin badago, bere umls kodeak lortu

# kodea non : $sct_id
# Oraingoz kategoria "reftype" moduan ipin dezaket baina 2 edo 3 daudenean, zer egin? Adib:
#<externalReferences>
#        <externalRef resource="SCT_es_INT_20131031" reference="116154003" reftype="trastorno">
#          <externalRef resource="UMLS-2010AB" reference="C0030705"/>
#        </externalRef>

# Errepikatu? edo leman "|" ipini? Oraingoz horrela?
# Dirudienez, hoberena errepikatzea da...

my $kat_ipini=0;
my $katak;


#Hashean bilatu bere balioak?
if (exists($ref_kategoriak->{$sct_id}))
{
    $kat_ipini=1;
    $katak=$ref_kategoriak->{$sct_id};
    # txukundu kategoriak
    $katak =~ s/ /_/g;
}


    #Zenbat elementu ditu reftypeak?
    #Gerta daiteke externalRef bat egotea reftype gabe ...
    my @refZatiak= split(/#/, $katak);
    if ($kat_ipini == 1 )
    {
	foreach my $kat (@refZatiak)
	{
	    my $xref = $ODOC->createElement("externalRef");
	    $xref->setAttribute("resource", "SCT_es_INT_20130430");
	    $xref->setAttribute("reference", $sct_id);
	    $xref->setAttribute("reftype", $kat); 
	
	foreach my $cui (@{ $hash_baliokide{$sct_id} }) {
	    my $xref2 = $ODOC->createElement("externalRef");
	    $xref2->setAttribute("resource", "UMLS-2010AB!");
	    $xref2->setAttribute("reference", $cui);
	    $xref->addChild($xref2);
	}
	$xrefs->addChild($xref);
	}
    } #if
    else
   {
    my $xref = $ODOC->createElement("externalRef");
    $xref->setAttribute("resource", "SCT_es_INT_20130430");
    $xref->setAttribute("reference", $sct_id);
    
   foreach my $cui (@{ $hash_baliokide{$sct_id} }) {
      my $xref2 = $ODOC->createElement("externalRef");
      $xref2->setAttribute("resource", "UMLS-2010AB!");
      $xref2->setAttribute("reference", $cui);
      $xref->addChild($xref2);
    }
    $xrefs->addChild($xref);
  } #else
}
}
}
}


sub KafOsatu
{

#<-------------------------------------------------- Beharrezko fitxategien pathak lortu  ----------------------------------------------------------->
my @pathak= pathak_lortu("Spa");
my $descriptionsFSNgabe=$pathak[0];
my $descriptionsFSNduna=$pathak[1];
my $sct_umls=$pathak[2];
my $sust_atc=$pathak[3]; 
# Talde terapeutiko batzuk
my $path="/usr/local/share/freeling/es_med/";

#<-------------------------------------------------------------- Hashak kargatu ------------------------------------------------------------------->
#print($pathak[0], $pathak[1], $pathak[2], $pathak[3]);
kargatu_sct_umls($path.$sct_umls,$ref_baliok);

kargatu_hashak($path.$descriptionsFSNgabe,$ref_bat,$ref_bi,$ref_hiru);

#Hemen kategoria adierazten duen hash-a kargatu beharko litzateke
kargatu_kategoriak($path.$descriptionsFSNduna, $ref_kategoriak);

kargatu_ATC($path.$sust_atc, $ref_katSust);

#<-------------------------------------------------- Etiketatzea -------------------------------------------------------------------------->



  
$emaitza= etiketatu($ref_bat,$ref_bi,$ref_hiru,$ref_baliok);
  


}
