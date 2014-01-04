#     Copyright 2014, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Generator for C++ and Python C/API.

This is the actual C++ code generator. It has methods and should be the only
place to know what C++ is like. Ideally it would be possible to replace the
target language by changing this one and the templates, and otherwise nothing
else.

"""

from .Indentation import (
    indented
)

# imported from here pylint: disable=W0611
from .LineNumberCodes import (
    getSetLineNumberCodeRaw,
    mergeLineNumberBranches,
    pushLineNumberBranch,
    popLineNumberBranch,
    getSetLineNumberCode,
    getLineNumberCode,
    resetLineNumber
)
from .ListCodes import (
    getListOperationAppendCode
)
from .DictCodes import (
    getDictOperationSetCode,
    getDictOperationGetCode,
    getDictOperationRemoveCode,
    getBuiltinDict2Code
)
from .SetCodes import (
    getSetOperationAddCode,
)

from .YieldCodes import (
    getYieldFromCode,
    getYieldCode
)

from .CallCodes import (
    getMakeBuiltinExceptionCode,
    getCallCodePosKeywordArgs,
    getCallCodePosArgsQuickC,
    getCallCodeKeywordArgs,
    getCallCodePosArgsC,
    getCallCodeNoArgsC,
    getCallsDecls,
    getCallsCode
)

from .ConstantCodes import (
    getConstantsInitCode,
    getConstantsDeclCode,
    getConstantAccessC,
    getConstantCode,
    needsPickleInit,
    stream_data
)

from .FunctionCodes import (
    getFunctionContextDefinitionCode,
    getDirectFunctionCallCode,
    getGeneratorFunctionCode,
    getFunctionCreationCode,
    getFunctionDirectDecl,
    getFunctionMakerCode,
    getFunctionMakerDecl,
    getFunctionCode,
)

from .IteratorCodes import (
    getBuiltinLoopBreakNextCode,
    getBuiltinNext1Code,
    getUnpackNextCode,
    getUnpackCheckCode,
)

from .ErrorCodes import (
    getErrorExitCode,
    getErrorExitBoolCode,
    getReleaseCodes,
    getReleaseCode
)

from .ExceptionCodes import (
    getTracebackMakingIdentifier,
    getExceptionIdentifier,
    getExceptionRefCode,
    getExceptionCaughtValueCode,
    getExceptionCaughtTypeCode,
    getExceptionCaughtTracebackCode,
    getExceptionUnpublishedReleaseCode
)

from .RaisingCodes import (
    getRaiseExceptionWithCauseCode,
    getRaiseExceptionWithValueCode,
    getRaiseExceptionWithTypeCode,
    getRaiseExceptionWithTracebackCode,
    getReRaiseExceptionCode,
)

from .PrintCodes import (
    getPrintNewlineCode,
    getPrintValueCode,
)

from .ModuleCodes import (
    getModuleMetapathLoaderEntryCode,
    getModuleDeclarationCode,
    getModuleAccessCode,
    getModuleIdentifier,
    getModuleCode
)

from .FrameCodes import (
    getFramePreserveExceptionCode,
    getFrameRestoreExceptionCode,
    getFrameReraiseExceptionCode,
    getFrameLocalsUpdateCode,
    getFrameGuardHeavyCode,
    getFrameGuardOnceCode,
    getFrameGuardLightCode
)

from .ImportCodes import (
    getImportNameCode,
    getImportModuleHardCode,
    getBuiltinImportCode,
    getImportFromStarCode
)

from .GlobalsLocalsCodes import (
    getLoadGlobalsCode,
    getLoadLocalsCode,
    getSetLocalsCode,
    getStoreLocalsCode,
)

from .ComparisonCodes import (
    getComparisonExpressionCode,
    getComparisonExpressionBoolCode,
    getBuiltinIsinstanceBoolCode,
    getBranchingCode
)

from .SliceCodes import (
    getSliceAssignmentIndexesCode,
    getSliceAssignmentCode,
    getSliceLookupIndexesCode,
    getSliceObjectCode,
    getSliceLookupCode,
    getSliceDelCode,
)

from .SubscriptCodes import (
    getIntegerSubscriptAssignmentCode,
    getSubscriptLookupCode,
    getSubscriptAssignmentCode,
    getSubscriptDelCode
)

from .AttributeCodes import (
    getAttributeCheckBoolCode,
    getSpecialAttributeLookupCode,
    getAttributeAssignmentClassSlotCode,
    getAttributeAssignmentDictSlotCode,
    getAttributeAssignmentCode,
    getAttributeLookupCode,
    getAttributeDelCode
)

from .IndexCodes import (
    getIndexValueCode,
    getIndexCode,
    getMinIndexCode,
    getMaxIndexCode,
)

from .LabelCodes import getGotoCode, getLabelCode

from .MainCodes import getMainCode

from .PythonAPICodes import getCAPIObjectCode, getCAPIIntCode

from .EvalCodes import (
    getCompileCode,
    getExecCode,
    getEvalCode
)

# imported from here pylint: enable=W0611

# These are here to be imported from here
# pylint: disable=W0611
from .VariableCodes import (
    getVariableAssignmentCode,
    getLocalVariableInitCode,
    getVariableAccessCode,
    getVariableDelCode,
    getVariableCode
)
# pylint: enable=W0611

from .CodeObjectCodes import (
    getCodeObjectsDeclCode,
    getCodeObjectsInitCode,
)

from . import (
    CodeTemplates,
    OperatorCodes,
    CppStrings
)

from nuitka import (
    Builtins,
    Utils
)


def getOperationCode(to_name, operator, arg_names, emit, context):
    # This needs to have one return per operation of Python, and there are many
    # of these, pylint: disable=R0911

    prefix_args = ()
    ref_count = 1

    if operator == "Pow":
        helper = "POWER_OPERATION"
    elif operator == "IPow":
        helper = "POWER_OPERATION_INPLACE"
    elif operator == "Add":
        helper = "BINARY_OPERATION_ADD"
    elif operator == "Sub":
        helper = "BINARY_OPERATION_SUB"
    elif operator == "Div":
        helper = "BINARY_OPERATION_DIV"
    elif operator == "Mult":
        helper = "BINARY_OPERATION_MUL"
    elif operator == "Mod":
        helper = "BINARY_OPERATION_REMAINDER"
    elif len(arg_names) == 2:
        helper = "BINARY_OPERATION"
        prefix_args = (
            OperatorCodes.binary_operator_codes[ operator ],
        )
    elif len(arg_names) == 1:
        impl_helper, ref_count = OperatorCodes.unary_operator_codes[ operator ]

        helper = "UNARY_OPERATION"
        prefix_args = (
            impl_helper,
        )
    else:
        assert False, operator

    emit(
        "%s = %s( %s );" % (
            to_name,
            helper,
            ", ".join(prefix_args + arg_names)
        )
    )

    for arg_name in arg_names:
        getReleaseCode(
            arg_name,
            emit,
            context
        )

    getErrorExitCode(
        check_name      = to_name,
        quick_exception = None,
        emit            = emit,
        context         = context
    )

    if ref_count:
        context.addCleanupTempName(to_name)


def getLoopBreakCode(emit, context):
    getExceptionUnpublishedReleaseCode(emit, context)

    break_target = context.getLoopBreakTarget()
    if type(break_target) is tuple:
        emit("%s = true;" % break_target[1])
        break_target = break_target[0]

    getGotoCode(break_target, emit)


def getLoopContinueCode(emit, context):
    getExceptionUnpublishedReleaseCode(emit, context)

    continue_target = context.getLoopContinueTarget()
    if type(continue_target) is tuple:
        emit("%s = true;" % continue_target[1])
        continue_target = continue_target[0]

    getGotoCode(continue_target, emit)


def getConditionCheckTrueCode(to_name, value_name, emit, context):
    emit(
        "%s = CHECK_IF_TRUE( %s );" % (
            to_name,
            value_name
        )
    )


def getConditionCheckFalseCode(to_name, value_name, emit, context):
    emit(
        "%s = CHECK_IF_FALSE( %s );" % (
            to_name,
            value_name
        )
    )


def getBuiltinRefCode(to_name, builtin_name, emit, context):
    emit(
        "%s = LOOKUP_BUILTIN( %s );" % (
            to_name,
            getConstantCode(
                constant = builtin_name,
                context  = context
            )
        )
    )

    getErrorExitCode(
        check_name = to_name,
        emit       = emit,
        context    = context
    )

    # Gives no reference


def getBuiltinAnonymousRefCode(to_name, builtin_name, emit, context):
    emit(
        "%s = (PyObject *)%s;" % (
            to_name,
            Builtins.builtin_anon_codes[ builtin_name ]
        )
    )


def getBuiltinSuperCode(to_name, type_name, object_name, emit, context):
    emit(
        "%s = BUILTIN_SUPER( %s, %s );" % (
            to_name,
            type_name if type_name is not None else "NULL",
            object_name if object_name is not None else "NULL"
        )
    )

    getReleaseCodes(
        release_names = (type_name, object_name),
        emit          = emit,
        context       = context
    )

    getErrorExitCode(
        check_name = to_name,
        emit       = emit,
        context    = context
    )

    context.addCleanupTempName(to_name)


def getBuiltinType3Code(to_name, type_name, bases_name, dict_name, emit,
                        context):
    emit(
        "%s = BUILTIN_TYPE3( %s, %s, %s, %s );" % (
            to_name,
            getConstantCode(
                constant = context.getModuleName(),
                context  = context
            ),
            type_name,
            bases_name,
            dict_name
        ),
    )

    getReleaseCodes(
        release_names = (type_name, bases_name, dict_name),
        emit          = emit,
        context       = context
    )

    getErrorExitCode(
        check_name = to_name,
        emit       = emit,
        context    = context
    )

    context.addCleanupTempName(to_name)


def getBuiltinLong2Code(to_name, base_name, value_name, emit, context):
    emit(
        "%s = TO_LONG2( %s, %s );" % (
            to_name,
            value_name,
            base_name
        )
    )

    getReleaseCodes(
        release_names = (value_name, base_name),
        emit          = emit,
        context       = context
    )

    getErrorExitCode(
        check_name = to_name,
        emit       = emit,
        context    = context
    )

    context.addCleanupTempName(to_name)


def getBuiltinInt2Code(to_name, base_name, value_name, emit, context):
    emit(
        "%s = TO_INT2( %s, %s );" % (
            to_name,
            value_name,
            base_name
        )
    )

    getReleaseCodes(
        release_names = (value_name, base_name),
        emit          = emit,
        context       = context
    )

    getErrorExitCode(
        check_name = to_name,
        quick_exception = None,
        emit       = emit,
        context    = context
    )

    context.addCleanupTempName(to_name)


def getExportScopeCode(cross_module):
    if cross_module:
        return "NUITKA_CROSS_MODULE"
    else:
        return "NUITKA_LOCAL_MODULE"


def _getMetaclassVariableCode(context):
    assert Utils.python_version < 300

    return "GET_STRING_DICT_VALUE( moduledict_%s, (Nuitka_StringObject *)%s )" % (
        context.getModuleCodeName(),
        getConstantCode(
            constant = "__metaclass__",
            context  = context
        )
    )


def getSelectMetaclassCode(to_name, metaclass_name, bases_name, emit, context):
    if Utils.python_version < 300:
        assert metaclass_name is None

        args = [
            bases_name,
            _getMetaclassVariableCode(context = context)
        ]
    else:
        args = [
            metaclass_name,
            bases_name
        ]


    emit(
        "%s = SELECT_METACLASS( %s );" % (
            to_name,
            ", ".join( args )
        )
    )

    # Can only fail with Python3.
    if Utils.python_version >= 300:
        getErrorExitCode(
            check_name = to_name,
            emit       = emit,
            context    = context
        )

        getReleaseCodes(
            release_names = args,
            emit          = emit,
            context       = context
        )
    else:
        getReleaseCode(
            release_name = bases_name,
            emit         = emit,
            context      = context
        )

    context.addCleanupTempName(to_name)


def getStatementTrace(source_desc, statement_repr):
    return 'puts( "Execute: " %s );' % (
        CppStrings.encodeString( source_desc + b" " + statement_repr ),
    )


def getConstantsDeclarationCode(context):
    constant_declarations, _constant_locals = getConstantsDeclCode(
        context    = context,
        for_header = True
    )

    constant_declarations += getCodeObjectsDeclCode(
        for_header = True
    )

    header_body = CodeTemplates.template_constants_declaration % {
        "constant_declarations" : "\n".join(constant_declarations)
    }

    return CodeTemplates.template_header_guard % {
        "header_guard_name" : "__NUITKA_DECLARATIONS_H__",
        "header_body"       : header_body
    }


def getConstantsDefinitionCode(context):
    constant_inits = getConstantsInitCode(
        context    = context
    )

    constant_inits += getCodeObjectsInitCode(
        context    = context
    )

    constant_declarations, constant_locals = getConstantsDeclCode(
        context    = context,
        for_header = False
    )

    constant_declarations += getCodeObjectsDeclCode(
        for_header = False
    )

    return CodeTemplates.template_constants_reading % {
        "constant_declarations" : "\n".join(constant_declarations),
        "constant_inits"        : indented(constant_inits),
        "constant_locals"       : indented(constant_locals)
    }
