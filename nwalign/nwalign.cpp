/*********************************************************************
Minimalist utility to use perform fast Needleman_Wunsch alignment outside of MindTheGap

Usage : nwalign < infile
Where infile is a two lines file with the two sequences to compare
Outputs identity score in stdout
*********************************************************************/
#define _GLIBCXX_USE_CXX11_ABI 0
#include <iostream>

using namespace std;


float needleman_wunsch(string a, string b, int * nbmatch,int * nbmis,int * nbgaps)
{
    float gap_score = -5;
    float mismatch_score = -5;
    float match_score = 10;
#define nw_score(x,y) ( (x == y) ? match_score : mismatch_score )

    int n_a = a.length(), n_b = b.length();
    float ** score =  (float **) malloc (sizeof(float*) * (n_a+1));
    for (int ii=0; ii<(n_a+1); ii++)
    {
        score [ii] = (float *) malloc (sizeof(float) * (n_b+1));
    }

	// float score[n_a+1][n_b+1];  //stack is too small
    // float pointer[n_a+1][n_b+1];

    for (int i = 0; i <= n_a; i++)
        score[i][0] = gap_score * i;
    for (int j = 0; j <= n_b; j++)
        score[0][j] = gap_score * j;

    // compute dp
    for (int i = 1; i <= n_a; i++)
    {
        for (int j = 1; j <= n_b; j++)
        {
            float match = score[i - 1][j - 1] + nw_score(a[i-1],b[j-1]);
            float del =  score[i - 1][j] + gap_score;
            float insert = score[i][j - 1] + gap_score;
            score[i][j] = max( max(match, del), insert);
        }
    }

    // traceback
    int i=n_a, j=n_b;
    float identity = 0;
	int nb_mis = 0;
	int nb_gaps = 0;

	int nb_end_gaps = 0 ;
	bool end_gap = true;

    while (i > 0 && j > 0)
    {

        float score_current = score[i][j], score_diagonal = score[i-1][j-1], score_up = score[i][j-1], score_left = score[i-1][j];
        if (score_current == score_diagonal + nw_score(a[i-1], b[j-1]))
        {
            if (a[i-1]== b[j-1])
			{

                identity++;
			}
			else
			{
				nb_mis++;
			}
            i -= 1;
            j -= 1;


			end_gap = false;
        }
        else
        {
            if (score_current == score_left + gap_score)
			{
				i -= 1;
			}
            else if (score_current == score_up + gap_score)
			{
				j -= 1;
			}


			if(!end_gap) //pour ne pas compter gap terminal
			{

				nb_gaps++;
			}
        }
    }

	//pour compter gaps au debut  :
	nb_gaps += i+j;
	//if(deb==1)printf("add gaps i j %i %i \n",i,j);

    identity /= max( n_a, n_b); // modif GR 27/09/2013    max of two sizes, otherwise free gaps

    if(nbmatch!=NULL) *nbmatch = identity;
    if(nbmis!=NULL)  *nbmis = nb_mis;
    if(nbgaps!=NULL) *nbgaps = nb_gaps;

    for (int ii=0; ii<(n_a+1); ii++)
    {
        free (score [ii]);
    }
    free(score);

    //printf("---nw----\n%s\n%s -> %.2f\n--------\n",a.c_str(),b.c_str(),identity);
    return identity;
}


int main (int argc, char* argv[])
{
    int nbLine = 0;
    string seq1;
    string seq2;

    float score;

    for (std::string line; std::getline(std::cin, line);) {
        nbLine += 1;
        if (nbLine == 1){
            seq1 = line;
        } else if (nbLine == 2){
            seq2 = line;
        } else{
            cout << "Only two lines expected" << endl;
            break;
        }
    }
    if (nbLine == 1){
        cout << "Input should be a two lines file with DNA sequences" << endl;
    }
    score = needleman_wunsch(seq1,seq2, NULL, NULL, NULL);
    cout << score << endl;
    return 0;

}