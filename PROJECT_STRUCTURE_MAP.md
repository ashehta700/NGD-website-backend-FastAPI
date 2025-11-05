# خريطة المسارات والصفحات في المشروع (SGS Website)

---

## جدول جميع المسارات (routes) والصفحات المرتبطة بها:

| المسار (Route)               | الـ Component                        | ملاحظات/حماية           |
|------------------------------|--------------------------------------|-------------------------|
| (رئيسي) ''                   | HomeComponent                        |                         |
| Home                         | HomeComponent                        |                         |
| About                        | AboutComponent                       |                         |
| Projects                     | AllProjectComponent                  |                         |
| Services                     | AllProductComponent                  |                         |
| geoInfoPortal                | geoInfoPortalComponent               |                         |
| webPortalQuestionnaire       | WebPortalQuestionnaireComponent      |                         |
| webPortalSurvey              | WebPortalSurveyComponent             | محمي بـ authGuard       |
| GeologicalMapsDatabase       | GeologicalMapsDatabaseComponent      |                         |
| News                         | AllNewsComponent                     |                         |
| News/:id                     | NewDetailsComponent                  |                         |
| LayerEarthData               | LayerEarthDataComponent              |                         |
| SupportAndAssistance         | SupportAndAssistanceComponent        |                         |
| ContactUs                    | ContactUsComponent                   |                         |
| UserManual                   | UserManualComponent                  |                         |
| GuideVideo                   | GuideVideosComponent                 |                         |
| FAQ                          | FAQComponent                         |                         |
| Products                     | ProductsComponent                    |                         |
| RSC                          | RSCComponent                         |                         |
| Geophysical                  | GeophysicalComponent                 |                         |
| AccountDetails               | AccountDetailsComponent              | محمي بـ authGuard       |
| FormBuilder                  | FormBuilderComponent                 |                         |
| RegisterVerification         | RegisterverificationComponent        |                         |
| ResetPassword                | ResetpasswordComponent               |                         |
| Dashboard                    | DashbordComponent                    | محمي بـ adminGuard      |
| ** (أي شيء غير معرف)         | - (Redirect إلى Home)                |                         |

---

## Tree Map (هيكلية المشروع بشكل شجري)

```
/ (الجذر) [HomeComponent]
├── Home                     [HomeComponent]
├── About                    [AboutComponent]
├── Projects                 [AllProjectComponent]
├── Services                 [AllProductComponent]
├── geoInfoPortal            [geoInfoPortalComponent]
├── webPortalQuestionnaire   [WebPortalQuestionnaireComponent]
├── webPortalSurvey          [WebPortalSurveyComponent | Protected: authGuard]
├── GeologicalMapsDatabase   [GeologicalMapsDatabaseComponent]
├── News                     [AllNewsComponent]
│   └── :id                  [NewDetailsComponent]
├── LayerEarthData           [LayerEarthDataComponent]
├── SupportAndAssistance     [SupportAndAssistanceComponent]
├── ContactUs                [ContactUsComponent]
├── UserManual               [UserManualComponent]
├── GuideVideo               [GuideVideosComponent]
├── FAQ                      [FAQComponent]
├── Products                 [ProductsComponent]
├── RSC                      [RSCComponent]
├── Geophysical              [GeophysicalComponent]
├── AccountDetails           [AccountDetailsComponent | Protected: authGuard]
├── FormBuilder              [FormBuilderComponent]
├── RegisterVerification     [RegisterverificationComponent]
├── ResetPassword            [ResetpasswordComponent]
├── Dashboard                [DashbordComponent | Protected: adminGuard]
└── ** (غير موجود/404)      [Redirect → Home]
```

---
