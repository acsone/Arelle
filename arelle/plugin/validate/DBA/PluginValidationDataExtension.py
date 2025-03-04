"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import cast

from arelle.ModelInstanceObject import ModelFact, ModelContext
from arelle.ModelValue import QName
from arelle.ModelXbrl import ModelXbrl
from arelle.utils.PluginData import PluginData


@dataclass
class PluginValidationDataExtension(PluginData):
    annualReportTypes: frozenset[str]
    assetsQn: QName
    auditedAssuranceReportsDanish: str
    auditedAssuranceReportsEnglish: str
    auditedExtendedReviewDanish: str
    auditedExtendedReviewEnglish: str
    auditedFinancialStatementsDanish: str
    auditedFinancialStatementsEnglish: str
    auditedNonAssuranceReportsDanish: str
    auditedNonAssuranceReportsEnglish: str
    averageNumberOfEmployeesQn: QName
    balanceSheetQnLessThanOrEqualToAssets: frozenset[QName]
    basisForAdverseOpinionDanish: str
    basisForAdverseOpinionEnglish: str
    basisForDisclaimerOpinionDanish: str
    basisForDisclaimerOpinionEnglish: str
    basisForQualifiedOpinionDanish: str
    basisForQualifiedOpinionEnglish: str
    classOfReportingEntityQn: QName
    consolidatedMemberQn: QName
    consolidatedSoloDimensionQn: QName
    dateOfApprovalOfAnnualReportQn: QName
    dateOfExtraordinaryDividendDistributedAfterEndOfReportingPeriod: QName
    dateOfGeneralMeetingQn: QName
    descriptionOfQualificationsOfAssuranceEngagementPerformedQn: QName
    descriptionsOfQualificationsOfReviewedFinancialStatementsQn: QName
    distributionOfResultsQns: frozenset[QName]
    employeeBenefitsExpenseQn: QName
    equityQn: QName
    extraordinaryCostsQn: QName
    extraordinaryIncomeQn: QName
    extraordinaryResultBeforeTaxQn: QName
    fr37RestrictedText: str
    hasNotGivenRiseToReservationsText: frozenset[str]
    identificationNumberCvrOfAuditFirmQn: QName
    independentAuditorsReportDanish: str
    independentAuditorsReportEnglish: str
    informationOnTypeOfSubmittedReportQn: QName
    liabilitiesQn: QName
    liabilitiesAndEquityQn: QName
    liabilitiesOtherThanProvisionsQn: QName
    longtermLiabilitiesOtherThanProvisionsQn: QName
    noncurrentAssetsQn: QName
    nameAndSurnameOfChairmanOfGeneralMeetingQn: QName
    nameOfAuditFirmQn: QName
    otherEmployeeExpenseQn: QName
    positiveProfitThreshold: float
    postemploymentBenefitExpenseQn: QName
    precedingReportingPeriodEndDateQn: QName
    precedingReportingPeriodStartDateQn: QName
    profitLossQn: QName
    proposedDividendRecognisedInEquityQn: QName
    proposedExtraordinaryDividendRecognisedInLiabilitiesQn: QName
    provisionsQn: QName
    reportingPeriodEndDateQn: QName
    reportingPeriodStartDateQn: QName
    shorttermLiabilitiesOtherThanProvisionsQn: QName
    signatureOfAuditorsDateQn: QName
    taxExpenseOnOrdinaryActivitiesQn: QName
    taxExpenseQn: QName
    typeOfAuditorAssistanceQn: QName
    typeOfBasisForModifiedOpinionOnFinancialStatementsReviewQn: QName
    typeOfReportingPeriodDimensionQn: QName
    wagesAndSalariesQn: QName

    _contextFactMap: dict[str, dict[QName, ModelFact]] | None = None
    _reportingPeriodContexts: list[ModelContext] | None = None

    def contextFactMap(self, modelXbrl: ModelXbrl) -> dict[str, dict[QName, ModelFact]]:
        if self._contextFactMap is None:
            self._contextFactMap = defaultdict(dict)
            for fact in modelXbrl.facts:
                self._contextFactMap[fact.contextID][fact.qname] = fact
        return self._contextFactMap

    def getCurrentAndPreviousReportingPeriodContexts(self, modelXbrl: ModelXbrl) -> list[ModelContext]:
        """
        :return: Returns the most recent reporting period contexts (at most two).
        """
        contexts = self.getReportingPeriodContexts(modelXbrl)
        if not contexts:
            return contexts
        if len(contexts) > 2:
            return contexts[-2:]
        return contexts

    def getReportingPeriodContexts(self, modelXbrl: ModelXbrl) -> list[ModelContext]:
        """
        :return: A sorted list of contexts that match "reporting period" criteria.
        """
        if self._reportingPeriodContexts is not None:
            return self._reportingPeriodContexts
        contexts = []
        for context in modelXbrl.contexts.values():
            context = cast(ModelContext, context)
            if context.isInstantPeriod or context.isForeverPeriod:
                continue  # Reporting period contexts can't be instant/forever contexts
            if len(context.qnameDims) > 0:
                if context.qnameDims.keys() != {self.consolidatedSoloDimensionQn}:
                    continue  # Context is dimensionalized with something other than consolidatedSoloDimensionQn
                if context.dimMemberQname(self.consolidatedSoloDimensionQn) != self.consolidatedMemberQn:
                    continue  # Context is dimensionalized with the correct dimension but not member
            contexts.append(context)
        self._reportingPeriodContexts = sorted(contexts, key=lambda c: c.endDatetime)
        return self._reportingPeriodContexts
