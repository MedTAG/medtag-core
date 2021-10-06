import spacy
import textdistance
import statistics
import itertools
import re
import operator
import pickle
import os

import utils

from tqdm import tqdm
from collections import Counter
from spacy.tokens import Span
from negspacy.negation import Negex
from scispacy.umls_linking import UmlsEntityLinker
from scispacy.abbreviation import AbbreviationDetector
from spacy_hunspell import spaCyHunSpell
from sklearn.metrics.pairwise import cosine_similarity


class BioNLP(object):

	def __init__(self, biospacy, rules, dysplasia_mappings, dict_path, aff_path):
		"""
		Load models and rules

		Params:
			biospacy (str): full spaCy pipeline for biomedical data
			rules (str): hand-crafted rules file path
			dysplasia_mappings (str): dysplasia mappings file path

		Returns: None
		"""	

		self.nlp = spacy.load(biospacy)

		abbreviation_pipe = AbbreviationDetector(self.nlp)  # add abbreviation detector to spaCy pipeline
		negex = Negex(self.nlp)  # add negation detector to spaCy pipeline
		hunspell = spaCyHunSpell(nlp, path=(dict_path, aff_path))  # add spell checker to spaCy pipeline
		self.linker = UmlsEntityLinker(k=10, max_entities_per_mention=2, resolve_abbreviations=True)  # tunable params - add umls entity linker to spaCy pipeline
		self.nlp.add_pipe(abbreviation_pipe, name="abbrv_detector")
		self.nlp.add_pipe(self.linker, after="abbrv_detector")  
		self.nlp.add_pipe(negex, last=True)
		self.nlp.add_pipe(self.expand_entity_mentions, name='expand_entities', after='ner')  # add expand_entity_mentions to spaCy processing pipeline
		self.nlp.add_pipe(hunspell)  # add hunspell to spaCy processing pipeline

		# load hand-crafted rules
		self.rules = utils.read_rules(rules)
		# set parameter to store the hand-crated rules restricted to a specific use-case (updated w/ self.set_rules() func)
		self.use_case_rules = dict()
		# set parameter to store candidate mentions from restricted rules
		self.use_case_candidates = list()

		# load dysplasia mappings
		self.dysplasia = utils.read_dysplasia_mappings(dysplasia_mappings)
		# set parameter to store dysplasia  mappings restricted to a specific use-case
		self.use_case_dysplasia = dict()


	### COMMON FUNCTIONS ###

	def spell_checker(self, text):
		"""
		Check input to find errors and return a list of suggestion words

		Params: 
			text (str): input text 

		Returns: dict of word suggestions for mispelled words {mis_word: [sug_word1, sug_word2, ...], ...}

		"""
		
		doc = self.nlp(text)
		suggestions = {word: word._.hunspell_suggest for word in doc if word._.hunspell_spell == False}
		return suggestions

	def update_rules(self, rules):
		"""
		Update self.hand_crafted_rules w/ rules contained within file

		Params:
			rules (str): rules file path

		Returns: loaded rules 
		"""

		self.rules = utils.read_rules(rules)
		return True

	def update_dysplasia_mappings(self, dysplasia_mappings):
		"""
		Update self.dysplasia_mappings w/ mappings contained within file

		Params:
			dysplasia_mappings (str): dysplasia mappings file path

		Returns: loaded mappings
		"""

		self.dysplasia = utils.read_dysplasia_mappings(dysplasia_mappings)
		return True

	def restrict2use_case(self, use_case):
		"""
		Restrict hand crafted rules to the considered use-case

		Params: 
			use_case (str): the considered use case

		Returns: the updated rules, candidates, and mappings
		"""

		self.use_case_rules = self.rules[use_case]
		self.use_case_candidates = [candidate for rule in self.use_case_rules.values() for candidate in rule[0]]
		self.use_case_dysplasia = self.dysplasia[use_case]
		return True

	def expand_entity_mentions(self, doc):  # @smarchesin TODO: add 3rd case when candidates can be either before or after target entity mention
		"""
		Expand entity mentions relying on hand-crafted rules

		Params:
			doc (spacy.tokens.doc.Doc): text processed w/ spaCy models

		Returns: a new set of entities for doc
		"""

		spans = list()
		# remove entity mentions that exact-match candidate mentions from rules
		ents = [ent for ent in doc.ents if (ent.text not in self.use_case_candidates)]
		# loop over restricted entities and expand entity mentions based on hand-crafted rules
		for ent in ents:
			# identify triggers for current entity mention
			triggers = [trigger for trigger in self.use_case_rules.keys() if (trigger in ent.text)]
			if triggers:
				# keep longest trigger as candidate trigger - e.g., adenocarcinoma instead of carcinoma, low-grade instead of low, etc.
				trigger = max(triggers, key=len)
				candidates, location = self.use_case_rules[trigger]
				# check whether the entity mention contains any rule's candidate 
				contained_candidates = [candidate for candidate in candidates if (candidate in ent.text)]
				if contained_candidates:  # entity mention contains rule's candidate
					spans.append([ent.start, ent.end])
				else:  # entity mention does not contain rule's candidates
					if location == 'PRE':  # candidates are matched on previous tokens 
						if ent.start != 0:  # entity mention does not start at beginning of doc
							matched_candidates = dict()
							for candidate in candidates:  # loop over candidates  
								num_tokens = len(candidate.split())  # number of tokens to inspect
								ix = self.skip_pre_punct(doc, ent.start-1) 
								if type(ix) == int:  # returns previous token index if not token.is_punct == True, otherwise None
									pre_tokens = doc[ix-num_tokens+1:ix+1]
									if candidate == pre_tokens.text:  # match between candidate and tokens
										matched_candidates[candidate] = (num_tokens, ix)
							if matched_candidates:
								# keep longest candidate for entity mention's expansion
								num_tokens, ix = matched_candidates[max(matched_candidates.keys(), key=len)]
								# expand entity mention
								spans.append([ix - num_tokens + 1, ent.end])
							else:
								# keep current entity mention as is
								spans.append([ent.start, ent.end])
						else:  # entity mention starts at beginning of doc
							# keep current entity mention as is
							spans.append([ent.start, ent.end])
					elif location == 'POST':  # candidates are matched on subsequent tokens 
						matched_candidates = dict()
						for candidate in candidates:
							num_tokens = len(candidate.split())  # number of tokens to inspect
							ix = self.skip_post_punct(doc, ent.end)
							if type(ix) == int:  # returns next token index if not token.is_punct == True, otherwise None
								post_tokens = doc[ix: ix + num_tokens]
								if candidate == post_tokens.text:  # match between candidate and tokens
									matched_candidates[candidate] = (num_tokens, ix)
						if matched_candidates:
							# keep longest candidate for entity mention's expansion
							num_tokens, ix = matched_candidates[max(matched_candidates.keys(), key=len)]
							# expand entity mention
							spans.append([ent.start, ix + num_tokens])
						else:
							# keep current entity mention as is
							spans.append([ent.start, ent.end])
			else:
				spans.append([ent.start, ent.end])
		if spans:  # doc contains valid entity mentions
			# merge entities w/ overlapping spans
			merged_spans = self.merge_spans(spans)
			doc.ents = [Span(doc, span[0], span[1], label='ENTITY') for span in merged_spans]
		return doc

	def skip_pre_punct(self, doc, ix):
		"""
		Get (recursively) the index of the precedent token where token.is_alpha == True

		Params:
			doc (spacy.tokens.doc.Doc): the processed document
			ix (int): the current index

		Returns: the correct token index or None if skip_punct meets EOS
		"""

		if ix == -1:  # BOS
			return None
		elif not doc[ix].is_punct:  # base case
			return ix
		else:  # recursive case
			return self.skip_pre_punct(doc, ix-1) 

	def skip_post_punct(self, doc, ix):
		"""
		Get (recursively) the index of the posterior token where token.is_alpha == True
		
		Params:
			doc (spacy.tokens.doc.Doc): the processed document
			ix (int): the current index
			
		Returns: the correct token index or None if skip_punct meets EOS
		"""
		
		if ix == len(doc):  # EOS
			return None
		elif not doc[ix].is_punct:  # base case
			return ix
		else:  # recursive case
			return self.skip_post_punct(doc, ix+1)

	def merge_spans(self, spans):
		"""
		Merge spans w/ overlapping ranges
		
		Params:
			spans (list(list)): list of span ranges [start, end]
			
		Returns: a list of merged span ranges [start, end]
		"""
		
		merged_spans = [spans[0]]
		for current in spans:
			previous = merged_spans[-1]
			if current[0] <= previous[1] - 1:
				previous[1] = max(previous[1], current[1])
			else:
				merged_spans.append(current)
		return merged_spans

	def extract_entity_mentions(self, text, keep_negated=False):
		"""
		Extract entity mentions identified within text.

		Params:
			text (str): text to be processed.
			keep_negated (bool): keep negated entity mentions

		Returns: a list of named/unnamed detected entity mentions
		"""

		doc = self.nlp(text)
		if keep_negated:  # keep negated mentions
			return [mention for mention in doc.ents]
		else: 
			return [mention for mention in doc.ents if mention._.negex == False]

	def extract_medical_abbreviations(self, text):
		"""
		Detects and resolves medical abbreviations within text

		Params:
			text (str): text to be processed.

		Returns: a list of abbrevations and their resolution
		"""

		doc = self.nlp(text)
		abbreviations = [(abrv, abrv._.long_form) for abrv in doc._.abbreviations]
		return abbreviations

	def link_mentions_to_UMLS(self, text, keep_negated=False):
		"""
		Extract entity mentions and link them to UMLS concepts

		Params:
			text (str): text to be processed

		Returns: CUIs associated to mentions w/ linking scores
		"""

		doc = self.nlp(text)
		if keep_negated:  # keep negated mentions
			mentions = [mention for mention in doc.ents]
		else:
			mentions = [mention for mention in doc.ents if mention._.negex == False]
		# link mentions to UMLS
		linked_mentions = list()
		for mention in mentions:
			cuis_and_scores = list()
			for umls_ent in mention._.umls_ents:
				# get CUI and score from umls_ents
				cui, score = umls_ent
				cuis_and_scores.append((cui, score))
			# store (mention, CUIs) for each entity mention
			linked_mentions.append((mention, cuis_and_scores))
		return linked_mentions			

	def text_similarity(self, mention, label):
		"""
		Compute different similarity measures between entity mention and concept label

		Params:
			mention (spacy.tokens.span.Span): entity mention extracted from text
			label (spacy.tokens.doc.Doc): concept label from ontology

		Returns: dict of similarity scores per metric plus aggregated score 
		"""

		sim_scores = dict()
		# compute similarity metrics
		sim_scores['ratcliff_obershelp'] = textdistance.ratcliff_obershelp.normalized_similarity(mention.text, label.text)
		sim_scores['word2vec'] = mention.similarity(label)
		return sim_scores

	def perform_linking(self, mention, labels, w2v_thr=0.7, ro_thr=0.5):
		"""
		Link target entity mention to ontology concepts 

		Params:
			mention (spacy.token.span.Span): entity mention extracted from text
			labels (list(spacy.token.span.Span)): list of concept labels from reference ontology
			w2v_thr (float): threshold to keep candidate labels matched using word2vec embeddings similarity
			ro_thr (float): threshold to keep candidate labels matched using ratcliff obershelp sub-string matching similarity

		Returns: matched ontology concept (or None)
		"""

		if 'dysplasia' in mention.text:  # mention contains 'dysplasia'
			return self.identify_dysplasia_grade(mention, labels)
		else:
			# perform similarity scores between the entity mention and the list of ontology labels
			scores_and_labels = [(self.text_similarity(mention, label), label.text) for label in labels]
			# keep labels w/ score greater or equal to word2vec threshold 
			scores_word2vec = [score_and_label for score_and_label in scores_and_labels if score_and_label[0]['word2vec'] >= w2v_thr]
			if not scores_word2vec:  # no match found
				return None
			elif len(scores_and_labels) > 1:  # matched mutiple candidate labels with word2vec
				# get word2vec candidate label w/ highest score
				best_word2vec = max(scores_word2vec, key=lambda score:score[0]['word2vec'])
				# keep labels w/ score greater or equal to string matching threshold
				scores_string_match = [score_and_label for score_and_label in scores_and_labels if score_and_label[0]['ratcliff_obershelp'] >= ro_thr]
				if not scores_string_match:  # no match found w/ string matching
					# keep word2vec canidate label with highest score
					return best_word2vec[1]
				else:  # compare word2vec candidates w/ string matching ones
					best_string_match = max(scores_string_match, key=lambda score:score[0]['ratcliff_obershelp'])
					if best_word2vec[1] == best_string_match[1]:  # cross-check: word2vec and string matching have the same best match
						return best_word2vec[1]
					else:  # cross-check: word2vec and string matching have different best matches
						if best_word2vec[0]['word2vec'] >= best_string_match[0]['ratcliff_obershelp']:  # keep word2vec candidate
							return best_word2vec[1]
						else:  # keep best matching candidate
							return best_string_match[1]
			else:  # link entity mention to the only candidate label matched
				return scores_word2vec[0][1]

	def link_mentions_to_concepts(self, mentions, labels, use_case_ontology, raw=False, w2v_thr=0.7, ro_thr=0.5):  # @smarchesin TODO: keep mention.text or shift to mention (SpaCy class)? 
		"""
		Link identified entity mentions to ontology concepts 

		Params:
			mentions (list(spacy.token.span.Span)): list of entity mentions extracted from text
			labels (list(spacy.token.span.Span)): list of concept labels from reference ontology
			use_case_ontology (pandas DataFrame): reference ontology restricted to the use case considered
			raw (bool): boolean to keep raw or cleaned version of linked concepts
			w2v_thr (float): threshold to keep candidate labels matched using word2vec embeddings similarity
			ro_thr (float): threshold to keep candidate labels matched using ratcliff obershelp sub-string matching similarity

		Returns: a dict of identified ontology concepts {semantic_area: [iri, mention, label], ...}
		"""

		# link mentions to concepts
		mentions_and_concepts = [(mention.text, self.perform_linking(mention, labels, w2v_thr=w2v_thr, ro_thr=ro_thr)) for mention in mentions]
		# extract linked data from ontology
		linked_data = [(mention_and_concept[0], use_case_ontology.loc[use_case_ontology['label'].str.lower() == mention_and_concept[1]][['iri', 'label', 'semantic_area_label']].values[0].tolist()) 
						for mention_and_concept in mentions_and_concepts if mention_and_concept[1] is not None]
		if raw:
			return linked_data
		else:
			# return linked concepts divided into semantic areas
			linked_concepts = {area: [] for area in set(use_case_ontology['semantic_area_label'].tolist()) if area is not None}
			for linked_datum in linked_data:
				linked_concepts[str(linked_datum[1][2])].append([linked_datum[1][0], linked_datum[1][1]])
			return linked_concepts

	def identify_dysplasia_grade(self, mention, labels):  # @smarchesin TODO: do we want to set a threshold score here?
		"""
		Identify (when possible) the dysplasia grade and link the dysplasia mention to the correct label 
		
		Params:
			mention (spacy.tokens.span.Span): (dysplasia) entity mention extracted from text
			labels (list(spacy.tokens.doc.Doc)): concept labels from ontology

		
		Returns: matched ontology concept (or None)
		"""
		
		dysplasia_mention = mention.text
		# identify candidates within dysplasia mappings
		candidates = [candidate for candidate in self.use_case_dysplasia.keys() if candidate in dysplasia_mention]
		if candidates:
			# get the longest dysplasia mapping matched
			candidate = max(candidates, key=len)
			# modify text mention by replacing the dysplasia grade w/ candidate mapping
			dysplasia_mention = dysplasia_mention.replace(candidate, self.use_case_dysplasia[candidate])
		# compute score to match mention w/ the appropriate label using substring matching
		scores_and_labels = [(textdistance.ratcliff_obershelp.normalized_similarity(dysplasia_mention, label.text), label.text) for label in labels]
		return max(scores_and_labels)[1]

	def process_ontology_concepts(self, labels):
		"""
		Process ontology labels using scispaCy

		Params:
			labels (list): list of concept labels

		Returns: a list of processed concept labels
		"""

		return [self.nlp(label) for label in labels]

	def lookup_snomed_codes(self, snomed_codes, use_case_ontology):
		"""
		Lookup for ontology concepts associated to target SNOMED codes

		Params:
			snomed_codes (list(str)/str): target SNOMED codes
			use_case_ontology (pandas DataFrame): reference ontology restricted to the use case considered

		Returns: a dict of identified ontology concepts {semantic_area: [iri, label], ...}
		"""
		
		lookups = {area: [] for area in set(use_case_ontology['semantic_area_label'].tolist()) if area is not None}
		if type(snomed_codes) == list:  # search for list of snomed codes
			snomed_codes = [code for code in snomed_codes if code]
			if snomed_codes:
				linked_data = use_case_ontology.loc[use_case_ontology['SNOMED'].isin(snomed_codes)][['iri', 'label', 'semantic_area_label']]
				if not linked_data.empty:  # matches found within ontology
					for linked_datum in linked_data.values.tolist():
						lookups[str(linked_datum[2])].append([linked_datum[0], linked_datum[1]])
			return lookups
		else:  # search for single snomed code
			if snomed_codes:
				linked_data = use_case_ontology.loc[use_case_ontology['SNOMED'] == snomed_codes][['iri', 'label', 'semantic_area_label']]
				if not linked_data.empty:  # match found within ontology
					linked_datum = linked_data.values[0].tolist()
					lookups[str(linked_datum[2])].append([linked_datum[0], linked_datum[1]])
			return lookups

	def online_entity_linking(self, report, onto_proc, labels, use_case, use_case_ontology):  # @smarchesin TODO: is there a better way to handle 'polyps' within 'materials' section?
		"""
		Perform entity linking over target report
		
		Params:
			report (dict): target report {'diagnosis': <string>, 'materials': <string>, 'codes': <list>, 'age': <string>, 'gender': <string>}
			onto_proc (OntologyProc): instance of OntologyProc class
			labels (list(spacy.tokens.doc.Doc)): list of processed ontology concepts
			use_case (str): the use_case considered - i.e. Colon, Lung, Uterine cervix, or celiac
			use_case_ontology (pandas.core.frame.DataFrame): ontology data restricted to given use case
			
		Returns: a dict containing the linked concepts for each report w/ distinction between 'nlp' and 'struct' concepts
		"""
		
		# extract entity mentions from 'diagnosis' sections
		mentions = self.extract_entity_mentions(utils.sanitize_record(report['diagnosis'], use_case))
		# consider 'polyp' as a stopwords in 'materials' section
		mentions += self.extract_entity_mentions(re.sub('polyp[s]?(\s|$)+', ' ', utils.sanitize_record(report['materials'], use_case)))
		# link and store 'nlp' concepts
		nlp_concepts = self.link_mentions_to_concepts(mentions, labels, use_case_ontology, raw=False)
		# link and store 'struct' concepts
		struct_concepts = self.lookup_snomed_codes([utils.sanitize_code(code) for code in report['codes']], use_case_ontology)
		# merge 'nlp' and 'struct' concepts 
		concepts = onto_proc.merge_nlp_and_struct(nlp_concepts, struct_concepts)
		# return concepts divided into 'nlp' and 'struct' sections (used for debugging, evaluation, and other applications)
		return concepts


	### AOEC SPECIFIC FUNCTIONS ###


	def batch_aoec_entity_linking(self, reports, onto_proc, labels, use_case, use_case_ontology):  # @smarchesin TODO: is there a better way to handle 'polyps' within 'materials' section?
		"""
		Perform entity linking over translated AOEC reports
		
		Params:
			reports (dict): target reports
			onto_proc (OntologyProc): instance of OntologyProc class
			labels (list(spacy.tokens.doc.Doc)): list of processed ontology concepts
			use_case (str): the use_case considered - i.e. Colon, Lung, Uterine cervix, or celiac
			use_case_ontology (pandas.core.frame.DataFrame): ontology data restricted to given use case
			
		Returns: a dict containing the linked concepts for each report w/ distinction between 'nlp' and 'struct' concepts
		"""
		
		concepts = dict()
		# loop over AOEC reports and perform linking
		for rid, rdata in tqdm(reports.items()):
			concepts[rid] = dict()
			# extract entity mentions from text sections
			mentions = self.extract_entity_mentions(utils.sanitize_record(rdata['diagnosis_nlp'], use_case))
			# consider 'polyp' as a stopwords in 'materials' section
			mentions += self.extract_entity_mentions(re.sub('polyp[s]?(\s|$)+', ' ', utils.sanitize_record(rdata['materials'], use_case)))
			# link and store 'nlp' concepts
			nlp_concepts = self.link_mentions_to_concepts(mentions, labels, use_case_ontology, raw=False)
			# link and store 'struct' concepts
			struct_concepts = self.lookup_snomed_codes([utils.sanitize_code(rdata['diagnosis_struct']), 
														utils.sanitize_code(rdata['procedure']), 
														utils.sanitize_code(rdata['topography'])], 
														use_case_ontology)
			# merge 'nlp' and 'struct' concepts 
			concepts[rid] = onto_proc.merge_nlp_and_struct(nlp_concepts, struct_concepts)
		# return concepts divided into 'nlp' and 'struct' sections (used for debugging, evaluation, and other applications)
		return concepts


	### RADBOUD SPECIFIC FUNCTIONS ###


	def batch_radboud_entity_linking(self, proc_reports, onto_proc, labels, use_case, use_case_ontology):  # @smarchesin TODO: add 'struct' part to the linking (use Radboud SNOMED codes) and decide whether to merge concepts between 'conclusions' and 'diagnosis'
		"""
		Perform entity linking over translated and processed Radboud reports

		Params:
			proc_reports (dict): target pre-processed reports 
			onto_proc (OntologyProc): instance of OntologyProc class
			labels (list(spacy.tokens.doc.Doc)): list of processed ontology concepts
			use_case (str): the use_case considered - i.e. Colon, Lung, Uterine cervix, or celiac
			use_case_ontology (pandas.core.frame.DataFrame): ontology data restricted to given use case

		Returns: a dict containing the linked concepts for each report w/ distinction between 'nlp' and 'struct' concepts
		"""
		
		concepts = dict()
		# loop over Radboud processed reports and perform linking
		for rid, rdata in tqdm(proc_reports.items()):
			concepts[rid] = dict()
			# loop over diagnoses
			for did, diagnosis in rdata.items():
				# extract entity mentions from diagnosis sections
				dmentions = [self.extract_entity_mentions(utils.sanitize_record(section, use_case)) for section in diagnosis[0]]
				# flatten mentions to a single list
				dmentions = list(itertools.chain.from_iterable(dmentions))
				# extract entity mentions from diagnosis-related conclusions
				cmentions = self.extract_entity_mentions(utils.sanitize_record(diagnosis[1][0], use_case))
				
				# link and store 'diagnosis' concepts 
				dconcepts = self.link_mentions_to_concepts(dmentions, labels, use_case_ontology, raw=False)
				# link and store 'conclusions' concepts
				cconcepts = self.link_mentions_to_concepts(cmentions, labels, use_case_ontology, raw=False)
				# merge 'diagnosis and 'conclusions' sections
				concepts[rid][did] = onto_proc.merge_diagnosis_and_conclusions(dconcepts, cconcepts)
		# return linked concepts divided per diagnosis
		return concepts 