"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

from typing import Optional, List, Dict, Set, Any

from django.db.models import Prefetch

from apps.common.log_utils import ProcessLogger, ErrorCollectingLogger
from apps.document.constants import FieldSpec
from apps.document.field_detection.field_based_ml_field_detection import \
    FieldBasedMLOnlyFieldDetectionStrategy, FieldBasedMLWithUnsureCatFieldDetectionStrategy
from apps.document.field_detection.fields_detection_abstractions import \
    DisabledFieldDetectionStrategy, FieldDetectionStrategy
from apps.document.field_detection.formula_and_field_based_ml_field_detection import \
    FormulaAndFieldBasedMLFieldDetectionStrategy
from apps.document.field_detection.formula_based_field_detection import FormulaBasedFieldDetectionStrategy
from apps.document.field_detection.python_coded_field_detection import PythonCodedFieldDetectionStrategy
from apps.document.field_detection.regexps_and_text_based_ml_field_detection import \
    RegexpsAndTextBasedMLFieldDetectionStrategy, TextBasedMLFieldDetectionStrategy
from apps.document.field_detection.regexps_field_detection import RegexpsOnlyFieldDetectionStrategy, \
    FieldBasedRegexpsDetectionStrategy
from apps.document.field_processing.field_processing_utils import order_field_detection, get_dependent_fields
from apps.document.field_types import TypedField
from apps.document.models import Document, DocumentType, DocumentField, ClassifierModel
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.repository.dto import FieldValueDTO
from apps.document.signals import fire_document_changed
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


STRATEGY_DISABLED = DisabledFieldDetectionStrategy()

_FIELD_DETECTION_STRATEGIES = [FieldBasedMLOnlyFieldDetectionStrategy(),
                               FieldBasedMLWithUnsureCatFieldDetectionStrategy(),
                               FormulaAndFieldBasedMLFieldDetectionStrategy(),
                               FormulaBasedFieldDetectionStrategy(),
                               RegexpsOnlyFieldDetectionStrategy(),
                               RegexpsAndTextBasedMLFieldDetectionStrategy(),
                               TextBasedMLFieldDetectionStrategy(),
                               PythonCodedFieldDetectionStrategy(),
                               FieldBasedRegexpsDetectionStrategy(),
                               STRATEGY_DISABLED]

FIELD_DETECTION_STRATEGY_REGISTRY = {st.code: st
                                     for st in _FIELD_DETECTION_STRATEGIES}  # type: Dict[str, FieldDetectionStrategy]


def train_document_field_detector_model(log: ProcessLogger,
                                        field: DocumentField,
                                        train_data_project_ids: Optional[List],
                                        use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
    strategy = FIELD_DETECTION_STRATEGY_REGISTRY[
        field.value_detection_strategy] \
        if field.value_detection_strategy else STRATEGY_DISABLED

    return strategy.train_document_field_detector_model(log,
                                                        field,
                                                        train_data_project_ids,
                                                        use_only_confirmed_field_values)


def detect_field_value(log: ProcessLogger,
                       doc: Document,
                       field: DocumentField,
                       save: bool = False) -> Optional[FieldValueDTO]:
    field_repo = DocumentFieldRepository()
    strategy = FIELD_DETECTION_STRATEGY_REGISTRY[
        field.value_detection_strategy] \
        if field.value_detection_strategy else STRATEGY_DISABLED

    doc_field_values = None

    depends_on_codes = set(field.get_depends_on_codes())

    if depends_on_codes:
        doc_field_values = field_repo.get_field_code_to_python_value(
            document_type_id=doc.document_type_id,
            doc_id=doc.pk,
            field_codes_only=depends_on_codes)

    dto = strategy.detect_field_value(log, doc, field, doc_field_values)
    if save and dto is not None:
        field_repo.update_field_value_with_dto(document=doc, field=field, field_value_dto=dto, user=None)
    return dto


def suggest_field_value(doc: Document, field: DocumentField) -> Any:
    log = ErrorCollectingLogger()
    field_value_dto = detect_field_value(log, doc=doc, field=field, save=False)
    log.raise_if_error()
    return field_value_dto.field_value if field_value_dto else None


class FieldDetectionError(Exception):
    pass


def detect_and_cache_field_values_for_document(log: ProcessLogger,
                                               document: Document,
                                               save: bool = True,
                                               clear_old_values: bool = True,
                                               changed_by_user: User = None,
                                               system_fields_changed: bool = False,
                                               generic_fields_changed: bool = False,
                                               document_initial_load: bool = False,
                                               ignore_field_codes: Set[str] = None,
                                               updated_field_codes: List[str] = None):
    """
    Detects field values for a document and stores their DocumentFieldValue objects as well as Document.field_value.
    These two should always be consistent.
    :param log:
    :param document:
    :param save:
    :param clear_old_values:
    :param changed_by_user
    :param system_fields_changed
    :param generic_fields_changed
    :param ignore_field_codes
    :param document_initial_load
    :param updated_field_codes - if set, we search for changed and dependent fields only
    :return:
    """
    import apps.document.repository.document_field_repository as dfr
    field_repo = dfr.DocumentFieldRepository()

    if save and document.status and not document.status.is_active:
        raise RuntimeError(f'Detecting field values for completed documents is not permitted.\n'
                           f'Document: {document.name} (#{document.pk})')

    document_type = document.document_type  # type: DocumentType

    all_fields = document_type.fields \
        .all() \
        .prefetch_related(Prefetch('depends_on_fields', queryset=DocumentField.objects.only('uid').all()))

    all_fields = list(all_fields)

    fields_and_deps = [(f.code, set(f.get_depends_on_codes()) or set()) for f in all_fields]
    dependent_fields = get_dependent_fields(fields_and_deps, set(updated_field_codes)) \
        if updated_field_codes else None

    sorted_codes = order_field_detection(fields_and_deps)
    all_fields_code_to_field = {f.code: f for f in all_fields}  # type: Dict[str, DocumentField]

    log.info(f'Detecting field values for document {document.name} (#{document.pk}), save={save}.\n'
             f'Updated fields: {updated_field_codes or "All"}.\n'
             f'Dependent fields to be detected: {dependent_fields or "All"}.\n'
             f'Ignored fields: {ignore_field_codes}.')

    if updated_field_codes:
        sorted_codes = [c for c in sorted_codes
                        if c in dependent_fields and (not ignore_field_codes or c not in ignore_field_codes)]
    elif ignore_field_codes:
        sorted_codes = [c for c in sorted_codes if c not in ignore_field_codes]

    current_field_values = {f.code: None for f in all_fields}
    # we may get values for fields required for sorted_codes, regarding
    # further dependencies
    # or we may just get all fields' values (field_codes_only=None)
    actual_field_values = field_repo.get_field_code_to_python_value(document_type_id=document_type.pk,
                                                                    doc_id=document.pk,
                                                                    field_codes_only=None)
    current_field_values.update(actual_field_values)

    res = list()

    detecting_field_status = []  # type:List[str]

    for field_code in sorted_codes:

        field = all_fields_code_to_field[field_code]  # type: DocumentField
        typed_field = TypedField.by(field)  # type: TypedField
        field_detection_strategy = FIELD_DETECTION_STRATEGY_REGISTRY[
            field.value_detection_strategy]  # type: FieldDetectionStrategy

        try:
            new_field_value_dto = field_detection_strategy.detect_field_value(log=log,
                                                                              doc=document,
                                                                              field=field,
                                                                              field_code_to_value=current_field_values)

            if not new_field_value_dto:
                detecting_field_status.append(f"No new value's gotten for '{field.code}'")
                continue
            if is_unit_limit_exceeded(new_field_value_dto, field, document):
                continue

            detecting_field_status.append(
                f"{format_value_short_str(new_field_value_dto.field_value)} for '{field.code}'")

            # now merge the detection results with the current DB state
            if save:
                # user = None here to store detected values as owned by system allowing further overwriting
                field_value, annotations = field_repo.update_field_value_with_dto(document=document,
                                                                                  field=field,
                                                                                  field_value_dto=new_field_value_dto,
                                                                                  user=None)

                # and update the field value of this field which may be used for detection of fields depending on it
                current_field_values[field.code] = typed_field.field_value_json_to_python(field_value.value)

            # If save is not requested then do not update current_field_values.
            # Most likely in this case we detect only few requested fields and trying to comply the dependency
            # tree makes no big sense.
        except Exception as e:
            msg = f'Unable to detect field value.\n' \
                f'Document type: {document_type.code}\n' \
                f'Document: {document.name} (#{document.pk})\n' \
                f'Field: {field.code}\n' \
                f'Field type: {typed_field.type_code}'
            raise FieldDetectionError(msg) from e

    if save:
        if updated_field_codes:
            user_fields_changed_set = set(updated_field_codes)
            if dependent_fields:
                user_fields_changed_set.update(dependent_fields)
            user_fields_changed = list(user_fields_changed_set)  # type: FieldSpec
        else:
            user_fields_changed = True

        fire_document_changed(sender=detect_and_cache_field_values_for_document,
                              log=log,
                              document=document,
                              changed_by_user=changed_by_user,
                              document_initial_load=document_initial_load,
                              system_fields_changed=system_fields_changed,
                              generic_fields_changed=generic_fields_changed,
                              user_fields_changed=user_fields_changed)
        if dependent_fields:
            msg = f'Recalculating dependent fields for {document.name}: '  # dependent_fields
            msg += ', '.join(dependent_fields)
            msg += '.\n\nSource fields data: \n'
            msg += '; '.join([f'"{k}": "{format_value_short_str(current_field_values[k])}"'
                              for k in current_field_values])
            msg += '.\n\nCalculation results:\n'
            msg += '\n'.join(detecting_field_status)
            log.info(msg)

    return res


def is_unit_limit_exceeded(fval_dto: FieldValueDTO,
                           field: DocumentField,
                           _: Document) -> bool:
    if not fval_dto.annotations or not field.detect_limit_count:
        return False
    # "filter" annotations by detect_limit_count
    if field.detect_limit_unit == DocumentField.DETECT_LIMIT_CHAR:
        fval_dto.annotations = [d for d in fval_dto.annotations
                                if d.location_in_doc_start <= field.detect_limit_count]
        return not (not field.requires_text_annotations or fval_dto.annotations)
    # TODO: we can't calculate other text measuring units (sentence, paragraph, page)
    # with reasonable effort
    return False


def format_value_short_str(val: Any) -> str:
    if val is None:
        return 'None'
    s = str(val)
    if len(s) < 128:
        return s
    return s[:70] + ' ... ' + s[len(s) - 40:]
