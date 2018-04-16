import py_entitymatching as em

# Load data files
A = em.read_csv_metadata('./TableA.csv', key='ID')
B = em.read_csv_metadata('./TableB.csv', key='ID')

# Create overlap blocker
ob = em.OverlapBlocker()
# Block rule 1: titles share more than three words, split by whitespaces
C = ob.block_tables(A, B, 'title', 'title', rem_stop_words = True, overlap_size = 3, 
	l_output_attrs=['title', 'author', 'isbn', 'publisher', 'edition', 'dimension'], 
	r_output_attrs=['title', 'author', 'isbn', 'publisher', 'edition', 'dimension'] )
# Block rule 2: authors share more than two words, split by whitespaces
D = ob.block_candset(C, 'author', 'author', rem_stop_words = True, overlap_size = 2)
# Debugging the 
dbg = em.debug_blocker(D, A, B, output_size=200)
dbg.head()

# Save Table D
#em.to_csv_metadata(D, './TableD.csv')

# Sample candidate set of size 300
S = em.sample_table(D, 300)
# Gold label
#G = em.label_table(S, label_column_name = 'gold_labels')
G = em.read_csv_metadata('./labeled.csv', key='_id', fk_ltable='ltable_ID', fk_rtable='rtable_ID', ltable = A, rtable = B)
# Split training set and test set
train_test = em.split_train_test(G, train_proportion=0.5)
I = train_test['train']
I['ltable_edition'] = ''
I['rtable_edition'] = ''
I['ltable_pages'] = ''
I['rtable_pages'] = ''
J = train_test['test']
J['ltable_edition'] = ''
J['rtable_edition'] = ''
J['ltable_pages'] = ''
J['rtable_pages'] = ''

# Save Set I
#em.to_csv_metadata(I, './TableI.csv')
# Save Set J
#em.to_csv_metadata(J, './TableJ.csv')

# Automatic feature generation
F = em.get_features_for_matching(A, B, validate_inferred_attr_types = False)
H = em.extract_feature_vecs(I, feature_table=F, attrs_after=['gold_labels'])
# Fill missing values
H.fillna(value='NaN', inplace=True)

# Create ML matchers
dt = em.DTMatcher(name='DecisionTree')
svm = em.SVMMatcher(name='SVM')
rf = em.RFMatcher(name='RandomForest')
lg = em.LogRegMatcher(name='LogisticRegression')
ln = em.LinRegMatcher(name='LinearRegression')
nb = em.NBMatcher(name='NaiveBayes')
# Select the best matcher
result = em.select_matcher([dt,rf, svm, ln, lg, nb], table=H, exclude_attrs=['_id', 'ltable_ID', 'rtable_ID', 'gold_labels'], k=5, target_attr='gold_labels', metric_to_select_matcher='f1')
print(result['cv_stats'])
best_matcher = result['selected_matcher']

# Evaluate the matcher
L = em.extract_feature_vecs(J, feature_table=F, attrs_after=['gold_labels'])
L.fillna(value='NaN', inplace=True)
best_matcher.fit(table=H, exclude_attrs=['_id', 'ltable_ID', 'rtable_ID', 'gold_labels'], target_attr='gold_labels')
predictions = best_matcher.predict(table=L, exclude_attrs=['_id', 'ltable_ID', 'rtable_ID', 'gold_labels'], target_attr='predicted_labels', append = True)
eval_result = em.eval_matches(predictions, 'gold_labels', 'predicted_labels')
print('----------Best Matcher: ', best_matcher.name, '----------')
em.print_eval_summary(eval_result)

# Evaluate other matcher
matchers = [dt, svm, rf, lg, ln, nb]
matchers_name = ['DecisionTree', 'SVM', 'RandomForest', 'LogisticRegression', 'LinearRegression', 'NaiveBayes']
for tool, name in zip(matchers, matchers_name):
    if(name == best_matcher.name):
        continue;
    tool.fit(table=H, exclude_attrs=['_id', 'ltable_ID', 'rtable_ID', 'gold_labels'], target_attr='gold_labels')
    pred = tool.predict(table=L, exclude_attrs=['_id', 'ltable_ID', 'rtable_ID', 'gold_labels','predicted_labels'], target_attr='predicted_labels', append = True)
    rlt = em.eval_matches(pred, 'gold_labels', 'predicted_labels')
    print('----------',name,'----------')
    em.print_eval_summary(rlt)














